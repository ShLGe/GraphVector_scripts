# Steps to Test TigerVector, Milvus, Neo4j, and Neptune Analytics

## 1. Prepare Vector and CSV Files
- Download vector files from the [Big ANN Benchmarks website](https://big-ann-benchmarks.com/neurips21.html).  
- Convert the downloaded vector files into CSV format using the provided script:  
  ```bash
  python3 convertor.py
  ```

## 2. Set Up Databases
- Select the database system to test.  
- For example, to test TigerVector, follow the instructions in `tigergraph/README.md` to complete the setup.

## 3. Run Performance Tests
- Specify the database system name in the script `recall.py`.  
- Execute the performance test:  
  ```bash
  python3 recall.py
  ```