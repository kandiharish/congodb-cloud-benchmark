# Multi-Database Architecture

## Core Design Principles
The benchmark harness normalizes database-specific query interfaces into a common workload contract. This ensures scalability of the test suite and fairness in the execution model. 

## The Adapter Pattern
Database-specific query syntax is isolated behind adapter implementations. Every database adapter in `src/databases/` implements the `BaseGraphAdapter` interface:

- `connect()`: Establishes a verified connection pool.
- `health_check()`: Verifies live database availability.
- `create_schema()`: Idempotent constraint and index setup.
- `load_nodes()` / `load_relationships()`: Optimized data ingestion pipelines.
- `validate_counts()`: Post-load integrity checks.
- `run_query()`: Standardized query execution endpoint.
- `close()`: Secure resource cleanup.

## Implementation Modules
1. **CognoDB, Neo4j, Memgraph**: Implemented via the official `neo4j` Python driver, sharing OpenCypher queries for optimal batching via `UNWIND`.
2. **FalkorDB**: Implemented via the native `falkordb` Python client, executing native RedisGraph-style queries.
3. **Apache AGE**: Implemented via `psycopg2`, executing Cypher queries over PostgreSQL connections.

## The Reporting Pipeline
The reporting pipeline produces normalized latency, throughput, and resource metrics. The main executor orchestrates multi-threaded operations and dynamically populates the `results/` directory with `raw` latency logs and `processed` JSON aggregations.
