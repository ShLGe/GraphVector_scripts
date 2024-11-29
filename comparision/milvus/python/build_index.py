
from pymilvus import Collection
from pymilvus import connections
import time
connections.connect(
  alias="default", 
  host='localhost', 
  port='19530'
)
collection = Collection("Element")      # Get an existing collection.
index_params = {
  "metric_type":"L2",
  "index_type":"HNSW",
  "params":{"M":16, "efConstruction":128}
}

# Record the start time
start_time = time.time_ns()
collection.create_index(
  field_name="vector", 
  index_params=index_params
)
# Record the end time
end_time = time.time_ns()

# Calculate the time consumed
total_time_microseconds = (end_time - start_time) / 1000
print(f"Time taken to build HNSW index: {total_time_microseconds} microseconds")
print(collection.indexes)
