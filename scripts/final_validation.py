import os
import hashlib
from collections import defaultdict, deque
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
    return adj_list

def extract_bfs_subset(adj_list, seed, target_edges):
    visited_nodes = {seed}
    queue = deque([seed])
    
    edges = []
    unique_nodes = {seed}
    duplicates = 0
    self_loops = 0
    
    seen_edges = set()

    while queue and len(edges) < target_edges:
        current = queue.popleft()
        
        # Sort neighbors for deterministic selection
        neighbors = sorted(adj_list.get(current, []))
        
        for neighbor in neighbors:
            if len(edges) >= target_edges:
                break
                
            if current == neighbor:
                self_loops += 1
                
            edge = (current, neighbor)
            if edge in seen_edges:
                duplicates += 1
            else:
                seen_edges.add(edge)
                edges.append(edge)
                
            unique_nodes.add(neighbor)
            
            if neighbor not in visited_nodes:
                visited_nodes.add(neighbor)
                queue.append(neighbor)
                
    return edges, unique_nodes, duplicates, self_loops

def get_hash(edges, nodes):
    # Canonicalize
    sorted_edges = sorted(edges)
    sorted_nodes = sorted(list(nodes))
    
    edge_str = "\n".join(f"{s},{d}" for s, d in sorted_edges)
    node_str = "\n".join(str(n) for n in sorted_nodes)
    
    edge_hash = hashlib.sha256(edge_str.encode()).hexdigest()
    node_hash = hashlib.sha256(node_str.encode()).hexdigest()
    
    return edge_hash, node_hash

def validate_age_for_subset(nodes, filepath):
    valid_ages = []
    missing_count = 0
    invalid_count = 0
    
    # We need to read line by line, 1-based index
    current_node = 1
    with open(filepath, 'r') as f:
        for line in f:
            if current_node in nodes:
                val = line.strip()
                if val == 'null' or val == '0':
                    missing_count += 1
                else:
                    try:
                        age = int(val)
                        valid_ages.append(age)
                    except ValueError:
                        invalid_count += 1
            current_node += 1
            
    return valid_ages, missing_count, invalid_count

def main():
    mtx_path = r"C:\cognodb-cloud-benchmark\data\downloads\archive\soc-Pokec.mtx"
    age_path = r"C:\cognodb-cloud-benchmark\data\downloads\archive\soc-Pokec_age.txt"
    
    adj_list = load_graph(mtx_path)
    
    seed = 1000
    target_edges = 130000
    
    print("--- RUN 1 ---")
    edges_1, nodes_1, dup_1, self_1 = extract_bfs_subset(adj_list, seed, target_edges)
    hash_e1, hash_n1 = get_hash(edges_1, nodes_1)
    
    print("--- RUN 2 ---")
    edges_2, nodes_2, dup_2, self_2 = extract_bfs_subset(adj_list, seed, target_edges)
    hash_e2, hash_n2 = get_hash(edges_2, nodes_2)
    
    print(f"\nEdges: {len(edges_1)}")
    print(f"Nodes: {len(nodes_1)}")
    print(f"Duplicates: {dup_1}")
    print(f"Self-loops: {self_1}")
    
    print(f"Run 1 edges hash: {hash_e1}")
    print(f"Run 2 edges hash: {hash_e2}")
    print(f"Run 1 nodes hash: {hash_n1}")
    print(f"Run 2 nodes hash: {hash_n2}")
    print(f"Identical: {'YES' if hash_e1 == hash_e2 and hash_n1 == hash_n2 else 'NO'}")
    
    # Validate dangling
    missing_endpoints = 0
    for u, v in edges_1:
        if u not in nodes_1 or v not in nodes_1:
            missing_endpoints += 1
    print(f"Missing endpoints: {missing_endpoints}")
    
    # Age validation
    print("\n--- AGE VALIDATION ---")
    valid_ages, missing, invalid = validate_age_for_subset(nodes_1, age_path)
    print(f"Selected nodes: {len(nodes_1)}")
    print(f"Valid ages: {len(valid_ages)}")
    print(f"Missing ages: {missing}")
    print(f"Invalid ages: {invalid}")
    
    if valid_ages:
        valid_ages.sort()
        print(f"Min age: {valid_ages[0]}")
        print(f"Max age: {valid_ages[-1]}")
        
        # Percentiles
        print(f"Median age: {valid_ages[len(valid_ages)//2]}")
        
        # Distribution checks
        over_18 = sum(1 for a in valid_ages if a >= 18)
        over_25 = sum(1 for a in valid_ages if a > 25)
        over_30 = sum(1 for a in valid_ages if a > 30)
        
        print(f"Selectivity >= 18: {(over_18/len(nodes_1))*100:.2f}%")
        print(f"Selectivity > 25: {(over_25/len(nodes_1))*100:.2f}%")
        print(f"Selectivity > 30: {(over_30/len(nodes_1))*100:.2f}%")

if __name__ == "__main__":
    main()
