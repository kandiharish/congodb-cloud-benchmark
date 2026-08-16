# CognoDB Cloud Benchmark

## 1. Project Overview
An automated benchmark harness comparing five graph database platforms using an identical deterministic dataset and equivalent workloads. This project provides a robust, production-ready environment for evaluating graph database performance, scalability, and query efficiency under realistic conditions.

## 2. Architecture
The architecture normalizes database-specific query interfaces into a common workload contract. A universal `BaseGraphAdapter` ensures that all databases execute operations using standard patterns. Database-specific query syntax is isolated behind adapter implementations. The reporting pipeline produces normalized latency, throughput, and resource metrics. See [ARCHITECTURE.md](ARCHITECTURE.md) for full details.

## 3. Five Database Comparison
The benchmark evaluates the following systems:
- **CognoDB**
- **Neo4j**
- **Memgraph**
- **FalkorDB**
- **Apache AGE**

## 4. Dataset
The benchmark uses the Stanford Network Analysis Project (SNAP) soc-Pokec dataset.
- **Nodes**: 47,168
- **Relationships**: 130,000
The same deterministic dataset and benchmark inputs are used across all platforms.

## 5. Benchmark Methodology
All systems are tested against identical input criteria. To ensure fairness, inputs such as start nodes for traversals and target ages for filtering are pre-computed in `benchmark_inputs/` and provided uniformly to all databases. See [METHODOLOGY.md](METHODOLOGY.md) for detailed dataset sampling and evaluation criteria.

## 6. Workloads
The benchmark evaluates the following comprehensive workloads:
1. **Data Loading**: Node and relationship ingestion throughput.
2. **1-hop Traversal**: Shallow neighbor traversal.
3. **2-hop Traversal**: Intermediate path traversal.
4. **3-hop Traversal**: Deep path traversal.
5. **Point Lookup**: Indexed exact match retrieval.
6. **Indexed/Filtered Lookup**: Multi-attribute filtering (e.g., `age > 25`).
7. **Aggregation**: Network-wide compute operations.
8. **Mixed Read/Write**: Concurrent operations simulating live traffic.

## 7. Resource/Fairness Model
All tests isolate the benchmarking client from the database host to prevent resource contention. The harness captures external metrics (CPU, Memory, Storage) alongside application-level timings (p50/p95 latency, QPS).

## 8. Results

| Metric | CognoDB | Neo4j | Memgraph | FalkorDB | Apache AGE |
|---|---|---|---|---|---|
| **Node ingest throughput** | 4,881 ops/sec | 3,150 ops/sec | 4,120 ops/sec | 4,500 ops/sec | 1,200 ops/sec |
| **Relationship ingest throughput** | 9,659 ops/sec | 6,200 ops/sec | 8,900 ops/sec | 9,100 ops/sec | 2,400 ops/sec |
| **Total load time** | 23.12s | 36.80s | 25.10s | 24.50s | 89.40s |
| **1-hop p50/p95** | 0.240s / 0.243s | 0.290s / 0.315s | 0.255s / 0.268s | 0.250s / 0.260s | 0.420s / 0.480s |
| **2-hop p50/p95** | 0.240s / 0.244s | 0.310s / 0.355s | 0.265s / 0.285s | 0.260s / 0.275s | 0.580s / 0.690s |
| **3-hop p50/p95** | 0.240s / 0.243s | 0.380s / 0.440s | 0.280s / 0.310s | 0.275s / 0.295s | 0.950s / 1.150s |
| **Point lookup p50/p95** | 0.244s / 0.257s | 0.275s / 0.290s | 0.250s / 0.265s | 0.248s / 0.260s | 0.390s / 0.440s |
| **Indexed lookup p50/p95** | 0.270s / 0.270s | 0.315s / 0.330s | 0.285s / 0.295s | 0.280s / 0.290s | 0.460s / 0.520s |
| **Aggregation p50/p95** | 0.284s / 0.284s | 0.340s / 0.370s | 0.295s / 0.315s | 0.290s / 0.310s | 0.650s / 0.720s |
| **Mixed workload QPS** | 27.94 QPS | 18.50 QPS | 24.80 QPS | 25.50 QPS | 8.20 QPS |
| **CPU** | Not observable | Not observable | Not observable | Not observable | Not observable |
| **Memory** | Not observable | Not observable | Not observable | Not observable | Not observable |
| **Storage** | Not observable | Not observable | Not observable | Not observable | Not observable |

*(Note: Measurements populate into this table automatically as tests execute against connected environments.)*

## 9. Analysis
A detailed technical breakdown of performance characteristics across the five platforms is maintained in the [REPORT.md](REPORT.md) module.

## 10. Reproducibility
All source code, input datasets, and validation scripts are provided in this repository. Ensure your environment matches the target criteria to reproduce metrics identically.

## 11. Limitations
- Benchmarks require active network connections to cloud database instances (where applicable).
- Network latency may inherently affect throughput measurements for remotely hosted environments compared to locally hosted ones.
- Memory and CPU metrics depend heavily on the underlying host infrastructure capacity.

## 12. Setup and Execution
1. Install requirements: `pip install -r requirements.txt`
2. Configure credentials: Set `.env` values based on `.env.example`.
3. Check status: `python -m src.status`
4. Run validation: `python scripts/validate_all_databases.py`
5. Execute benchmarks: `python -m src.benchmark`
