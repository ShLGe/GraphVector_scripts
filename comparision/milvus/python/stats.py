from pymilvus import connections, Collection, utility

# Connect to Milvus
connections.connect()

# Get an existing collection
collection = Collection("Element")

# Get the query segment info
segment_info = utility.get_query_segment_info(collection_name="Element")

# Print the segment information
for segment in segment_info:
    print(segment)

print(len(segment_info))
total_rows = collection.num_entities
print(f"Total number of rows in the collection : {total_rows}")
