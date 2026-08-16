import os
from collections import defaultdict, deque
import sys
import gc

def load_graph(filepath):
    print("Loading graph into memory...")
    adj_list = defaultdict(list)
    with open(filepath, 'r') as f:
        for line in f:
            if line.startswith('%'):
                continue
            parts = line.split()
            if len(parts) == 2:
                src, dst = int(parts[0]), int(parts[1])
                adj_list[src].append(dst)
    print(f"Graph loaded. Nodes with outgoing edges: {len(adj_list)}")
    return adj_list

def test_bfs_seed(adj_list, seed, target_edges=130000):
    if seed not in adj_list:
        return {"seed": seed, "error": "Seed not in graph"}
        
    visited_nodes = {seed}
    queue = deque([(seed, 0)]) # (node, depth)
    
    collected_edges = 0
    max_depth = 0
    unique_nodes = {seed}
    duplicates = 0
    self_loops = 0
    
    # We want exactly target_edges, but we process node by node.
    # To be precise, we can stop mid-node if we hit the limit, but usually we add all edges of a node.
    # Let's add edge by edge.
    
    while queue and collected_edges < target_edges:
        current, depth = queue.popleft()
        max_depth = max(max_depth, depth)
        
        for neighbor in adj_list.get(current, []):
            if current == neighbor:
                self_loops += 1
            
            # Add edge
            collected_edges += 1
            unique_nodes.add(neighbor)
            
            if neighbor not in visited_nodes:
                visited_nodes.add(neighbor)
                queue.append((neighbor, depth + 1))
                
            if collected_edges >= target_edges:
                break
                
    return {
        "seed": seed,
        "edges": collected_edges,
        "nodes": len(unique_nodes),
        "max_depth": max_depth,
        "density": collected_edges / len(unique_nodes) if unique_nodes else 0,
        "fits": len(unique_nodes) < 50000 and 100000 <= collected_edges <= 175000,
        "self_loops": self_loops,
        "disconnected": 0 # Not tracking disconnected since BFS only finds connected
    }

def validate_age(filepath):
    print("\nValidating age property...")
    valid_ages = []
    missing_count = 0
    invalid_count = 0
    total_lines = 0
    
    with open(filepath, 'r') as f:
        for line in f:
            total_lines += 1
            val = line.strip()
            if val == 'null' or val == '0':
                missing_count += 1
            else:
                try:
                    age = int(val)
                    valid_ages.append(age)
                except ValueError:
                    invalid_count += 1
                    
    print(f"Total records: {total_lines}")
    print(f"Missing values (null or 0): {missing_count}")
    print(f"Invalid values: {invalid_count}")
    
    if valid_ages:
        print(f"Min age: {min(valid_ages)}")
        print(f"Max age: {max(valid_ages)}")
        
        # Selectivity check > 25
        over_25 = sum(1 for a in valid_ages if a > 25)
        print(f"Users over 25: {over_25} ({(over_25/total_lines)*100:.2f}% of total)")

def main():
    mtx_path = r"C:\cognodb-cloud-benchmark\data\downloads\archive\soc-Pokec.mtx"
    age_path = r"C:\cognodb-cloud-benchmark\data\downloads\archive\soc-Pokec_age.txt"
    
    adj_list = load_graph(mtx_path)
    
    seeds = [1, 100, 1000, 10000, 50000, 100000]
    
    print("\n--- BFS SEED EXPERIMENT ---")
    print(f"{'Seed':>8} | {'Edges':>8} | {'Nodes':>8} | {'Depth':>5} | {'Density':>7} | {'Fits?':>5}")
    print("-" * 60)
    
    for seed in seeds:
        res = test_bfs_seed(adj_list, seed, 130000)
        if "error" in res:
            print(f"{seed:>8} | {res['error']}")
        else:
            print(f"{res['seed']:>8} | {res['edges']:>8} | {res['nodes']:>8} | {res['max_depth']:>5} | {res['density']:>7.2f} | {str(res['fits']):>5}")
            
    # Clear memory
    del adj_list
    gc.collect()
    
    validate_age(age_path)

if __name__ == "__main__":
    main()
