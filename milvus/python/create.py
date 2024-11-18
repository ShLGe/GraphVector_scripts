from pymilvus import CollectionSchema, FieldSchema, DataType, Collection
from pymilvus import connections
connections.connect(
  alias="default", 
  host='localhost', 
  port='19530'
)
id = FieldSchema(
  name="id", 
  dtype=DataType.INT64, 
  is_primary=True, 
)

vector = FieldSchema(
  name="vector", 
  dtype=DataType.FLOAT_VECTOR, 
  dim=768
)
schema = CollectionSchema(
  fields=[id, vector], 
)
collection_name = "Element_2"

collection = Collection(
    name=collection_name, 
    schema=schema, 
    )

print(collection.schema)
print(collection.indexes)

# Output
#
# {
#     "state": "<LoadState: NotLoad>"
# }