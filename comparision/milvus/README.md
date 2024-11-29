# Steps to Test Milvus

## 1. Configure Milvus
- Access the Milvus Docker container and modify the configuration file:
  ```bash
  sudo docker exec -it milvus-standalone bash
  vim configs/milvus.yaml
  ```
  - Adjust the gRPC receive max size and segment max size settings as needed.


## 2. Restart Milvus
- Restart the Milvus service to apply the configuration changes:
  ```bash
  bash standalone_embed.sh restart
  ```

## 3. Insert Data
- Use raw vector files to insert data into Milvus:
  ```bash
  python3 milvus/python/insert.py
  ```

## 4. Build Index
- Build the index for the inserted data:
  ```bash
  python3 milvus/python/build_index.py
  ```

## 5. Verify Segment Number
- Perform a warmup and verify the segment number:
  ```bash
  python3 milvus/python/warmup.py
  python3 milvus/python/stats.py
  ```

## 6. Test Recall Rate
- Evaluate recall rates under different `ef` settings. 
  Commands:
  ```bash
  python3 milvus/python/release.py
  python3 milvus/python/warmup.py
  ```