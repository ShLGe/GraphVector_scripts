from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType
import csv

# Milvus connection details
milvus_host = "localhost"
milvus_port = "19530"

# Connect to Milvus
connections.connect(alias="default", host=milvus_host, port=milvus_port)

# Define Milvus collection schema
fields = [
    FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=False),
    FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=128)  # Adjust dim to match your vector dimension
]
schema = CollectionSchema(fields, "Element collection schema")

# Create or load the collection
collection_name = "element_collection"
collection_exists = collection_name in connections.list_collections()
if collection_exists:
    collection = Collection(name=collection_name)
else:
    collection = Collection(name=collection_name, schema=schema)

def load_csv_to_milvus(csv_file):
    ids = []
    embeddings = []
    
    # Read the CSV file and prepare data for Milvus insertion
    with open(csv_file, newline='') as file:
        reader = csv.reader(file)
        for row in reader:
            element_id = int(row[0])  # Assuming the ID is in the first column
            embedding = [float(x) for x in row[1:]]  # Convert embedding values to float
            ids.append(element_id)
            embeddings.append(embedding)
    
    # Insert data into the Milvus collection
    collection.insert([ids, embeddings])
    collection.flush()

# File path to your CSV
csv_file = "/home/graphsql/tigergraph_test/dataset/sift/csv_dataset/sift_base.csv"

# Load CSV data into Milvus
load_csv_to_milvus(csv_file)

# Close the Milvus connection
connections.disconnect(alias="default")
