import pandas as pd
from pymilvus import connections, Collection
import time

# Step 1: Connect to Milvus
connections.connect("default", host="localhost", port="19530")

# Step 2: Load your CSV file
csv_file_path = '/home/graphsql/dataset/bigann/bigann10M_base.csv'
data = pd.read_csv(csv_file_path, header=None, names=["id", "embedding"])  # Adjust if CSV has headers

# Step 3: Prepare the data for Milvus (depends on your collection schema)
collection_name = 'Element'
collection = Collection(collection_name)

start_time = time.time_ns()
# Extract data from the CSV
ids = data['id'].tolist()
embeddings = data['embedding'].apply(lambda x: list(map(float, x.split(':')))).tolist()  # Split by ':' and convert to floats

# Calculate and print the total time taken for data preparation
end_time = time.time_ns()
total_time_microseconds = (end_time - start_time) / 1000
print(f"Time taken to convert: {total_time_microseconds} microseconds")

start_time = time.time_ns()
# Step 4: Insert data into Milvus in fixed batch size
batch_size = 31250
for i in range(0, len(ids), batch_size):
    
    # Get the current batch
    batch_ids = ids[i:i + batch_size]
    batch_embeddings = embeddings[i:i + batch_size]

    collection.insert([batch_ids, batch_embeddings])
    collection.flush()  # Flush after each batch

end_time = time.time_ns()

# Calculate and print the total time taken in microseconds
total_time_microseconds = (end_time - start_time) / 1000
print(f"Time taken to insert: {total_time_microseconds} microseconds")
