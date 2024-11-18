step to test Neo4j

# import dataset
sudo neo4j-admin database import full neo4j --delimiter="," --array-delimiter=":" --nodes=Element=/home/graphsql/dataset/bigann/bigann_header.csv,/home/graphsql/dataset/bigann/bigann100M_base.csv --overwrite-destination

# restart database to see imported data
sudo neo4j restart

# login cypher
cypher-shell -u neo4j -p lsgneo4j123

# create index and wait
python3 neo4j_test/python/create_index.py

# use RESTAPI to query
python3 neo4j_test/python/recall.py
