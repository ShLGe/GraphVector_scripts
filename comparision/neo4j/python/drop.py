from neo4j import GraphDatabase

# Define Neo4j connection details
uri = "bolt://localhost:7687"
username = "neo4j"
password = ""

# Connect to the Neo4j database
driver = GraphDatabase.driver(uri, auth=(username, password))

def drop_all_nodes(tx):
    # Cypher query to delete all nodes
    tx.run("MATCH (n) DETACH DELETE n")

# Function to drop all nodes
def drop_all():
    with driver.session() as session:
        session.write_transaction(drop_all_nodes)
    print("All nodes have been deleted.")

# Execute the drop_all function
drop_all()

# Close the Neo4j connection
driver.close()
