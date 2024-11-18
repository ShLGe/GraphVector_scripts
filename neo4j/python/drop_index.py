from neo4j import GraphDatabase

# Replace with your Neo4j connection details
uri = "bolt://localhost:7687"
username = "neo4j"
password = "lsgneo4j123"

def drop_vector_index():
    driver = GraphDatabase.driver(uri, auth=(username, password))
    
    with driver.session() as session:
        try:
            # Cypher command to drop the vector index
            session.run("DROP INDEX element_embedding_index")
            print("Index 'element_embedding_index' dropped successfully.")
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            driver.close()

if __name__ == "__main__":
    drop_vector_index()
