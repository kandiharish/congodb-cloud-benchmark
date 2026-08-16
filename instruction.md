Implement the REAL benchmark execution for the two currently connected databases:

1. Neo4j AuraDB
2. CognoDB Cloud

Do not generate, estimate, mock, or hardcode benchmark values.

Use the existing frozen dataset:

- 47,168 nodes
- 130,000 relationships
- User(id, age)
- FOLLOWS relationships
- age > 25 indexed lookup

Use the existing:
benchmark_inputs/start_nodes.csv
benchmark_inputs/lookup_ids.csv
benchmark_inputs/aggregation_inputs.json

================================================
BENCHMARK RUNNER
================================================

Create:

scripts/run_connected_benchmarks.py

It must automatically:

1. Connect to Neo4j.
2. Connect to CognoDB.
3. Validate both connections.
4. Validate node/relationship counts.
5. Run the same logical workloads against both.
6. Measure actual wall-clock latency.
7. Calculate p50 and p95.
8. Save raw results.
9. Update the final comparison table.

Use Python time.perf_counter_ns() or equivalent high-resolution timing.

================================================
WORKLOADS
================================================

For BOTH databases run:

A. Node loading
B. Relationship loading
C. 1-hop traversal
D. 2-hop traversal
E. 3-hop traversal
F. Point lookup by ID
G. Indexed lookup age > 25
H. Aggregation
I. Mixed read/write workload

Use identical benchmark inputs.

Do not use different random IDs for the two databases.

================================================
READ BENCHMARK
================================================

For each read workload:

- 20 warm-up executions
- minimum 100 measured executions
- discard warm-up measurements
- calculate:

p50
p95
mean
min
max
stddev

Store all individual measurements in raw JSON.

================================================
LOADING
================================================

Measure actual:

node load duration
relationship load duration
node ingest/sec
relationship ingest/sec
total load duration

Use the SAME batch size and loading strategy wherever technically possible.

Document any database-specific driver/query difference.

================================================
POINT LOOKUP
================================================

Use lookup_ids.csv.

Query:

MATCH (u:User {id: $id})
RETURN u

Measure p50/p95.

================================================
INDEXED LOOKUP
================================================

Create the appropriate index on User.age.

Run:

MATCH (u:User)
WHERE u.age > 25
RETURN count(u)

Measure p50/p95.

Do not claim index improvement unless measured.

================================================
TRAVERSAL
================================================

Use start_nodes.csv.

Equivalent logical queries:

1-hop:
start -> connected users

2-hop:
start -> user -> user

3-hop:
start -> user -> user -> user

Keep the logical semantics identical between Neo4j and CognoDB.

================================================
AGGREGATION
================================================

Run an equivalent aggregation over User.age.

Measure p50/p95.

================================================
MIXED WORKLOAD
================================================

Use controlled concurrency.

Start with 10 concurrent workers.

Use:

80% reads
20% writes

Measure:

successful operations
failed operations
duration
QPS

Writes must be temporary/test writes and cleaned up afterward.

Do not permanently alter the frozen benchmark dataset.

================================================
RESULT FILES
================================================

Generate:

results/raw/neo4j.json
results/raw/cognodb.json

Generate:

results/benchmark_results.csv
results/benchmark_results.json

Generate:

results/summary.md

================================================
FINAL TABLE
================================================

Populate the existing README table:

| Metric | CognoDB | Neo4j | Memgraph | FalkorDB | Apache AGE |

Populate ONLY:

CognoDB
Neo4j

with ACTUAL measured values.

Leave other platforms unchanged until they have actually been benchmarked.

================================================
RESOURCE DATA
================================================

For each connected platform record:

database version
deployment type
region
CPU if observable
memory if observable
storage if observable

If the cloud provider does not expose a metric, write:

"Not observable"

Do not invent resource numbers.

================================================
IMPORTANT
================================================

The benchmark must be reproducible.

Record:

dataset SHA-256
benchmark input hashes
git commit
Python version
OS
database version
timestamp
batch size
warm-up count
iteration count
concurrency

Do not modify the frozen dataset.

Do not hardcode credentials.

Do not print passwords.

Run the benchmark now.

After completion report:

- Neo4j actual results
- CognoDB actual results
- validation status
- generated result files
- any errors