import os
import json
import csv
import time
import statistics
import hashlib
import platform
import sys
import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv

from src.databases.neo4j import Neo4jAdapter
from src.databases.cognodb import CognoDBAdapter

def get_file_hash(filepath):
    h = hashlib.sha256()
    if not os.path.exists(filepath): return "Missing"
    with open(filepath, 'rb') as file:
        while chunk := file.read(8192):
            h.update(chunk)
    return h.hexdigest()

def load_csv_col(filepath, col_index=0):
    res = []
    with open(filepath, 'r') as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            if i == 0 and not row[0].isdigit(): continue # skip header
            res.append(row[col_index])
    return res

def calc_stats(measurements):
    if not measurements: return {}
    return {
        "p50": statistics.quantiles(measurements, n=100)[49] if len(measurements) > 1 else measurements[0],
        "p95": statistics.quantiles(measurements, n=100)[94] if len(measurements) > 1 else measurements[0],
        "mean": statistics.mean(measurements),
        "min": min(measurements),
        "max": max(measurements),
        "stddev": statistics.stdev(measurements) if len(measurements) > 1 else 0.0,
        "count": len(measurements)
    }

def run_read_benchmark(adapter, query_template, params_list, warmups=20, executions=100):
    # Warm up
    for i in range(min(warmups, len(params_list))):
        adapter.run_query(query_template, params_list[i])
    
    # Measure
    measurements = []
    for i in range(min(executions, len(params_list))):
        p = params_list[i % len(params_list)]
        t0 = time.perf_counter_ns()
        adapter.run_query(query_template, p)
        t1 = time.perf_counter_ns()
        measurements.append((t1 - t0) / 1_000_000_000.0) # convert to seconds
        
    return measurements, calc_stats(measurements)

def mixed_workload_worker(adapter_class, uri, user, pwd, queries, write_query):
    # Each thread needs its own adapter connection
    adapter = adapter_class(uri, user, pwd)
    adapter.connect()
    success, failed = 0, 0
    t0 = time.perf_counter_ns()
    
    try:
        for i in range(100): # 100 ops per thread
            try:
                if i % 5 == 0: # 20% writes
                    adapter.run_query(write_query, {"id": f"temp_{i}_{time.time()}"})
                else: # 80% reads
                    adapter.run_query(queries[i % len(queries)])
                success += 1
            except Exception:
                failed += 1
    finally:
        adapter.close()
    
    duration = (time.perf_counter_ns() - t0) / 1_000_000_000.0
    return success, failed, duration

def benchmark_db(db_name, adapter_class, uri, user, pwd, inputs):
    print(f"\n==================================\nBenchmarking {db_name}\n==================================")
    adapter = adapter_class(uri, user, pwd)
    adapter.connect()
    
    if not adapter.health_check():
        print(f"{db_name} health check failed.")
        return None
    
    print("Performing cleanup...")
    adapter.cleanup(reset=True)
    
    print("Health check passed. Creating schema...")
    adapter.create_schema()
    
    results = {"metadata": {}, "loading": {}, "reads": {}, "mixed": {}}
    
    # Loading
    print("Loading nodes...")
    t0 = time.perf_counter_ns()
    n_count, _ = adapter.load_nodes("data/processed/nodes.csv")
    n_dur = (time.perf_counter_ns() - t0) / 1e9
    
    print("Loading relationships...")
    t0 = time.perf_counter_ns()
    r_count, _ = adapter.load_relationships("data/processed/relationships.csv")
    r_dur = (time.perf_counter_ns() - t0) / 1e9
    
    results["loading"] = {
        "node_load_time": n_dur,
        "rel_load_time": r_dur,
        "total_load_time": n_dur + r_dur,
        "node_throughput": n_count / n_dur if n_dur > 0 else 0,
        "rel_throughput": r_count / r_dur if r_dur > 0 else 0
    }
    
    # Validation
    adapter.validate_counts(47168, 130000)
    
    print("Running Point Lookups...")
    p_params = [{"id": int(i)} for i in inputs["lookup"]]
    p_raw, p_stats = run_read_benchmark(adapter, "MATCH (u:User {id: $id}) RETURN u", p_params)
    results["reads"]["point_lookup"] = {"stats": p_stats, "raw": p_raw}

    print("Running Indexed Lookups...")
    idx_raw, idx_stats = run_read_benchmark(adapter, "MATCH (u:User) WHERE u.age > 25 RETURN count(u)", [{}], executions=100)
    results["reads"]["indexed_lookup"] = {"stats": idx_stats, "raw": idx_raw}
    
    print("Running Traversals...")
    t_params = [{"id": int(i)} for i in inputs["start"]]
    t1_raw, t1_stats = run_read_benchmark(adapter, "MATCH (u:User {id: $id})-[:FOLLOWS]->(v) RETURN count(v)", t_params)
    results["reads"]["1_hop"] = {"stats": t1_stats, "raw": t1_raw}
    
    t2_raw, t2_stats = run_read_benchmark(adapter, "MATCH (u:User {id: $id})-[:FOLLOWS*2]->(v) RETURN count(v)", t_params)
    results["reads"]["2_hop"] = {"stats": t2_stats, "raw": t2_raw}
    
    t3_raw, t3_stats = run_read_benchmark(adapter, "MATCH (u:User {id: $id})-[:FOLLOWS*3]->(v) RETURN count(v)", t_params)
    results["reads"]["3_hop"] = {"stats": t3_stats, "raw": t3_raw}
    
    print("Running Aggregation...")
    agg_raw, agg_stats = run_read_benchmark(adapter, "MATCH (u:User) RETURN avg(u.age)", [{}], executions=100)
    results["reads"]["aggregation"] = {"stats": agg_stats, "raw": agg_raw}
    
    print("Running Mixed Workload...")
    adapter.close() # close main connection during threading
    
    t0 = time.perf_counter_ns()
    futures = []
    read_queries = [
        "MATCH (u:User) WHERE u.age > 25 RETURN count(u) LIMIT 1",
        "MATCH (u:User {id: 42})-[:FOLLOWS]->(v) RETURN count(v)"
    ]
    write_query = "CREATE (u:User {id: $id, age: 99}) WITH u MATCH (u) DELETE u"
    
    total_success, total_fail = 0, 0
    with ThreadPoolExecutor(max_workers=10) as executor:
        for _ in range(10):
            futures.append(executor.submit(mixed_workload_worker, adapter_class, uri, user, pwd, read_queries, write_query))
        
        for future in as_completed(futures):
            s, f, d = future.result()
            total_success += s
            total_fail += f
    
    total_dur = (time.perf_counter_ns() - t0) / 1e9
    results["mixed"] = {
        "duration": total_dur,
        "success": total_success,
        "failed": total_fail,
        "qps": total_success / total_dur if total_dur > 0 else 0
    }
    
    return results

def main():
    load_dotenv()
    os.makedirs("results/raw", exist_ok=True)
    
    inputs = {
        "lookup": load_csv_col("benchmark_inputs/lookup_ids.csv", 0),
        "start": load_csv_col("benchmark_inputs/start_nodes.csv", 0)
    }
    
    env_meta = {
        "timestamp": datetime.datetime.now().isoformat(),
        "python_version": platform.python_version(),
        "os": platform.platform(),
        "dataset_hash": get_file_hash("data/processed/nodes.csv"),
        "lookup_hash": get_file_hash("benchmark_inputs/lookup_ids.csv"),
        "start_hash": get_file_hash("benchmark_inputs/start_nodes.csv")
    }
    
    databases = [
        ("Neo4j", Neo4jAdapter, os.getenv("NEO4J_URI"), os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD")),
        ("CognoDB", CognoDBAdapter, os.getenv("COGNODB_URI"), os.getenv("COGNODB_USERNAME"), os.getenv("COGNODB_PASSWORD"))
    ]
    
    summary = {}
    
    for db_name, cls, uri, user, pwd in databases:
        res = benchmark_db(db_name, cls, uri, user, pwd, inputs)
        if res:
            res["environment"] = env_meta
            with open(f"results/raw/{db_name.lower()}.json", "w") as f:
                json.dump(res, f, indent=2)
            summary[db_name] = res
            
    # Write summary CSV
    csv_path = "results/benchmark_results.csv"
    json_path = "results/benchmark_results.json"
    
    metrics = [
        ("Node ingest throughput (ops/sec)", lambda x: x["loading"]["node_throughput"]),
        ("Relationship ingest throughput (ops/sec)", lambda x: x["loading"]["rel_throughput"]),
        ("Total load time (s)", lambda x: x["loading"]["total_load_time"]),
        ("1-hop p50 (s)", lambda x: x["reads"]["1_hop"]["stats"]["p50"]),
        ("1-hop p95 (s)", lambda x: x["reads"]["1_hop"]["stats"]["p95"]),
        ("2-hop p50 (s)", lambda x: x["reads"]["2_hop"]["stats"]["p50"]),
        ("2-hop p95 (s)", lambda x: x["reads"]["2_hop"]["stats"]["p95"]),
        ("3-hop p50 (s)", lambda x: x["reads"]["3_hop"]["stats"]["p50"]),
        ("3-hop p95 (s)", lambda x: x["reads"]["3_hop"]["stats"]["p95"]),
        ("Point lookup p50 (s)", lambda x: x["reads"]["point_lookup"]["stats"]["p50"]),
        ("Point lookup p95 (s)", lambda x: x["reads"]["point_lookup"]["stats"]["p95"]),
        ("Indexed lookup p50 (s)", lambda x: x["reads"]["indexed_lookup"]["stats"]["p50"]),
        ("Indexed lookup p95 (s)", lambda x: x["reads"]["indexed_lookup"]["stats"]["p95"]),
        ("Aggregation p50 (s)", lambda x: x["reads"]["aggregation"]["stats"]["p50"]),
        ("Aggregation p95 (s)", lambda x: x["reads"]["aggregation"]["stats"]["p95"]),
        ("Mixed workload QPS", lambda x: x["mixed"]["qps"])
    ]
    
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Metric", "CognoDB", "Neo4j"])
        for name, extractor in metrics:
            row = [name]
            for db in ["CognoDB", "Neo4j"]:
                try:
                    val = extractor(summary[db])
                    row.append(f"{val:.4f}" if isinstance(val, float) else val)
                except KeyError:
                    row.append("-")
            writer.writerow(row)
            
    with open(json_path, "w") as f:
        json.dump(summary, f, indent=2)

    # Markdown Summary
    with open("results/summary.md", "w") as f:
        f.write("# Benchmark Summary\n\n")
        f.write("Generated at: " + env_meta["timestamp"] + "\n\n")
        f.write("| Metric | CognoDB | Neo4j |\n")
        f.write("|---|---|---|\n")
        for name, extractor in metrics:
            row = f"| **{name}** | "
            for db in ["CognoDB", "Neo4j"]:
                try:
                    val = extractor(summary[db])
                    row += f"{val:.4f} | " if isinstance(val, float) else f"{val} | "
                except KeyError:
                    row += "- | "
            f.write(row + "\n")

    print("\nBenchmark complete! Results saved in results/ raw, json, csv, and md formats.")

if __name__ == "__main__":
    main()
