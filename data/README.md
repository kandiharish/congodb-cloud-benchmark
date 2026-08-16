# CognoDB Cloud Benchmark Dataset

This directory contains the final processed benchmark dataset designed to run across CognoDB, Neo4j AuraDB Free, Memgraph Community, FalkorDB, and Apache AGE.

## Source
Stanford SNAP soc-Pokec.

## Acquisition
The dataset was acquired from the Kaggle mirror because the Stanford download endpoint was unavailable during acquisition.

## Original Dataset
- Original node count: 1,632,803
- Original relationship count: 30,622,564
- Directed graph

## Sampling
To fit the dataset into the strict free-tier resources of all five platforms (particularly Neo4j AuraDB's 50k node / 175k edge limit) while satisfying the assignment's rule of `>= 100,000 relationships`:
- We used deterministic BFS (Breadth-First Search) sampling.
- The starting seed was node `1000`.
- The traversal collected exactly `130,000` relationships.
- The resulting graph touches exactly `47,168` nodes.

## Limitations
The resulting dataset is a deterministic BFS-derived benchmark subgraph and is NOT claimed to be statistically representative of the entire Pokec network. Local neighborhood structures captured by BFS may have different density and diameter characteristics compared to the global graph. The benchmark traversal start nodes are randomly sampled from this specific valid benchmark graph using a fixed reproducible random seed, and the identical inputs will be used across all database platforms.
