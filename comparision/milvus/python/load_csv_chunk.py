import pandas as pd
from pymilvus import connections, Collection
import time

# Step 1: Connect to Milvus
connections.connect("default", host="localhost", port="19530")

# Step 2: Prepare for chunked CSV reading
csv_file_path = '/home/graphsql/dataset/bigann/bigann100M_base.csv'
chunk_size = 10416670  # Adjust chunk size based on memory availability

# Step 3: Define collection details
collection_name = 'Element'
collection = Collection(collection_name)
convert_time = 0
insert_time = 0

# Step 4: Read and process the CSV file in chunks
for chunk in pd.read_csv(csv_file_path, header=None, names=["id", "embedding"], chunksize=chunk_size):
    start_time = time.time_ns()
    
    # Extract data from the chunk
    ids = chunk['id'].tolist()
    embeddings = chunk['embedding'].apply(lambda x: list(map(float, x.split(':')))).tolist()  # Convert to floats

    # Calculate and print the time taken for data preparation
    end_time = time.time_ns()
    total_time_microseconds = (end_time - start_time) / 1000
    convert_time += total_time_microseconds
    print(f"Time taken to convert chunk: {total_time_microseconds} microseconds")

    # Step 5: Insert data into Milvus in batches from the chunk
    batch_size = 1041667
    start_time = time.time_ns()
    for i in range(0, len(ids), batch_size):
        # Get the current batch
        batch_ids = ids[i:i + batch_size]
        batch_embeddings = embeddings[i:i + batch_size]

        collection.insert([batch_ids, batch_embeddings])
        collection.flush()  # Flush after each batch

    end_time = time.time_ns()
    
    # Calculate and print the total time taken in microseconds
    total_time_microseconds = (end_time - start_time) / 1000
    insert_time += total_time_microseconds
    print(f"Time taken to insert chunk: {total_time_microseconds} microseconds")

print(f"Time taken to convert: {convert_time} microseconds")
print(f"Time taken to insert: {insert_time} microseconds")
