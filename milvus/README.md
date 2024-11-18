step to test Milvus

# get into milvus docker, vim configs/milvus.yaml to config. should adjust gRPC receive max size and segment max size
sudo docker exec -it milvus-standalone bash

# Then restart milvus 
bash standalone_embed.sh restart

# prepare csv file. and load csv file. Each load and flush batch should be equal to expected segment size
python3 milvus/python/load_csv.py
python3 milvus/python/load_csv_chunk.py

# insert using numpy file
python3 milvus/python/insert.py

# build index
python3 milvus/python/build_index.py

# verify the segment number. Warmup and then print
python3 milvus/python/warmup.py
python3 milvus/python/stats.py

# test recall rate under different ef. remember, if go back from a large ef to a smaller ef, you should release and warmup again.
# otherwise the recall rate will be higher
python3 milvus/python/release.py
python3 milvus/python/warmup.py

# reload milvus segment. now test QPS and latency under different concurrency and different recall rate
python3 milvus/python/recall_process.py