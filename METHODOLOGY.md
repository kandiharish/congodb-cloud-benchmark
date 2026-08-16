# Benchmark Methodology

## Dataset Overview
The benchmark utilizes the SNAP soc-Pokec dataset, a well-known social network graph that provides realistic topology, highly connected nodes, and varied community structures.

### Dataset Parameters
- **Nodes**: 47,168
- **Relationships**: 130,000
- **Format**: Pre-processed CSV files (`nodes.csv`, `relationships.csv`)

## Deterministic Execution
To guarantee fairness, the evaluation employs deterministic inputs for all query workloads:
- **`benchmark_inputs/start_nodes.csv`**: Specific node IDs used as starting points for 1-hop, 2-hop, and 3-hop traversals.
- **`benchmark_inputs/lookup_ids.csv`**: Target IDs used for point lookups.
- **`benchmark_inputs/aggregation_inputs.json`**: Pre-defined filtering bounds for aggregations.

By using an identical deterministic dataset and equivalent workloads, the benchmark ensures that variations in performance are strictly attributable to the database engine and adapter, rather than data skew or random input variations.

## Measurement and Fairness Model
1. **Isolation**: The benchmark client runs separately from the database host.
2. **Warm-up Cycles**: The harness executes queries without recording metrics during an initial warm-up phase to ensure memory caches and execution plans are fully populated.
3. **Statistical Aggregation**: Latency metrics are recorded over thousands of iterations. The final results capture the 50th percentile (p50) and 95th percentile (p95) to accurately reflect both average performance and tail latency.
4. **Normalized Adapters**: The harness interfaces with all databases through a unified `BaseGraphAdapter`, ensuring uniform timing mechanisms.
