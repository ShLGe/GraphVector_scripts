from neo4j import GraphDatabase

# Define Neo4j connection details
uri = "bolt://localhost:7687"  # Update if necessary
username = "neo4j"
password = "lsgneo4j123"

# Connect to the Neo4j database
driver = GraphDatabase.driver(uri, auth=(username, password))

def create_vector_index(tx):
    # Cypher command to create a vector index
    cypher_query = """
    CREATE VECTOR INDEX element_embedding_index
    FOR (e:Element)
    ON e.embedding
    OPTIONS {
      indexConfig: {
        `vector.dimensions`: 128,
        `vector.similarity_function`: 'euclidean',
        `vector.quantization.enabled`: false,
        `vector.hnsw.m`: 16,
        `vector.hnsw.ef_construction`: 128
      }
    };
    """
    # Run the Cypher query
    tx.run(cypher_query)

def get_index_status(tx):
    # Cypher query to retrieve index details
    query = """
    CALL db.indexes() YIELD name, type, labelsOrTypes, properties, state
    RETURN name, type, labelsOrTypes, properties, state
    """
    result = tx.run(query)
    # Collect and return results
    indexes = []
    for record in result:
        indexes.append({
            "name": record["name"],
            "type": record["type"],
            "labelsOrTypes": record["labelsOrTypes"],
            "properties": record["properties"],
            "state": record["state"]
        })
    return indexes

def main():
    with driver.session() as session:
        # Create the vector index with the specified settings
        session.write_transaction(create_vector_index)
        #session.write_transaction(get_index_status)
        print("Vector index created successfully")
        

# Run the script
if __name__ == "__main__":
    main()

# Close the Neo4j connection
driver.close()
