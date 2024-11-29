# Steps to Test TigerGraph

## 1. Download and Install TigerGraph
- Follow the installation guide on the TigerGraph official website to download and set up TigerGraph.

## 2. Prepare and Load CSV Files
- Prepare the CSV files for data loading.
- Execute the following commands to create the schema and load data:
  ```bash
  gsql tigergraph/load/create.gsql
  gsql tigergraph/load/load.gsql
  ```
  - Wait for the indexing process to complete before proceeding.

## 3. Install Query
- Install the required query:
  ```bash
  gsql tigergraph/gsql/query.gsql
  ```
