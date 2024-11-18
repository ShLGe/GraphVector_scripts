step to test TigerGraph
# download and install TigerGraph

# prepare csv file. and load csv file. Wait for index building
gsql tigergraph/load/create.gsql
gsql tigergraph/load/load.gsql


# install query 
gsql tigergraph/gsql/query.gsql

# reload milvus segment. now test QPS and latency under different concurrency and different recall rate
python3 tigergraph/python/recall_process.py