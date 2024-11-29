from pymilvus import connections, Collection
import requests

# Step 1: Connect to Milvus
connections.connect("default", host="localhost", port="19530")

# Step 2: Retrieve the collection
collection_name = "Element"  # Replace with your collection name
collection = Collection(collection_name)
collection.load()
# Step 3: Load the collection to access its segments
print(dir(collection))
print(collection.indexes)



