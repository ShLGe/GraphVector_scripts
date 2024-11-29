from pymilvus import Collection
from pymilvus import connections
connections.connect(
  alias="default", 
  host='localhost', 
  port='19530'
)
# Load the collection
collection = Collection("Element")

# Drop the index
collection.drop_index()

collection.drop()
