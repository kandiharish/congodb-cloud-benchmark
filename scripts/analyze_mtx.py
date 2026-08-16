import os
import random

def analyze_graph(filepath):
    total_edges = 0
    unique_src = set()
    unique_dst = set()
    unique_nodes = set()
    self_loops = 0
    duplicates = 0
    seen_edges = set()

    # Strategy A evaluation variables
    first_150k_nodes = set()
    first_150k_edges = 0

    print(f"Analyzing {filepath}...")
    
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('%') or len(line.split()) > 2:
                continue
                
            parts = line.split()
            if len(parts) == 2:
                src, dst = parts
                total_edges += 1
                
                if total_edges <= 150000:
                    first_150k_edges += 1
                    first_150k_nodes.add(src)
                    first_150k_nodes.add(dst)

                unique_src.add(src)
                unique_dst.add(dst)
                unique_nodes.add(src)
                unique_nodes.add(dst)

                if src == dst:
                    self_loops += 1

                edge = (src, dst)
                if edge in seen_edges:
                    duplicates += 1
                else:
                    seen_edges.add(edge)
                    
            if total_edges >= 1000000:
                break
                
    print("--- SAMPLE GRAPH STATS (First 1M Edges) ---")
    print(f"Total Edges Processed: {total_edges}")
    print(f"Unique Sources: {len(unique_src)}")
    print(f"Unique Destinations: {len(unique_dst)}")
    print(f"Unique Nodes Total: {len(unique_nodes)}")
    print(f"Self-loops: {self_loops}")
    print(f"Duplicates: {duplicates}")

    print("\n--- FIRST 150K EDGES STATS (STRATEGY A) ---")
    print(f"Edges: {first_150k_edges}")
    print(f"Unique Nodes: {len(first_150k_nodes)}")

if __name__ == "__main__":
    analyze_graph(r"C:\cognodb-cloud-benchmark\data\downloads\archive\soc-Pokec.mtx")
