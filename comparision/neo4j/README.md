# Steps to Test Neo4j

## 1. Import Dataset
- Use the following command to import the dataset into Neo4j:
  ```bash
  sudo neo4j-admin database import full neo4j \
      --delimiter="," --array-delimiter=":" \
      --nodes=Element=/home/graphsql/dataset/bigann/bigann_header.csv,/home/graphsql/dataset/bigann/bigann100M_base.csv \
      --overwrite-destination
  ```

## 2. Restart Database
- Restart the Neo4j database to load the imported data:
  ```bash
  sudo neo4j restart
  ```

## 3. Log in to Cypher Shell
- Access the Cypher shell for query execution:
  ```bash
  cypher-shell
  ```

## 4. Create Index
- Run the script to create the index and wait for it to complete:
  ```bash
  python3 neo4j_test/python/create_index.py
  ```
