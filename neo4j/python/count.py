from neo4j import GraphDatabase

# Define Neo4j connection details
uri = "bolt://localhost:7687"  # Update if necessary
username = "neo4j"
password = ""

# Connect to the Neo4j database
driver = GraphDatabase.driver(uri, auth=(username, password))

def count_nodes(tx):
    # Run the Cypher query to count all nodes
    result = tx.run("MATCH (n) RETURN COUNT(n) AS node_count")
    # Return the result
    return result.single()["node_count"]

def fetch_node_by_id(tx, node_id):
    # Run the Cypher query to fetch a node by its internal Neo4j ID
    result = tx.run("MATCH (n) WHERE ID(n) = $id RETURN n", id=node_id)
    # Return the node
    return result.single()

def main():
    with driver.session() as session:
        # Execute the query to count all nodes
        node_count = session.read_transaction(count_nodes)
        print(f"Total number of nodes: {node_count}")
        
        # Fetch the node with ID 1
        node = session.read_transaction(fetch_node_by_id, 1)
        if node:
            print(f"Node with ID 1: {node['n']}")
        else:
            print("Node with ID 1 not found")

# Run the script
if __name__ == "__main__":
    main()

# Close the Neo4j connection
driver.close()
