from neo4j import GraphDatabase

# Replace with your Neo4j connection details
uri = "bolt://localhost:7687"
username = "neo4j"
password = "lsgneo4j123"

# Function to get node labels and their counts
def get_node_counts(uri, username, password):
    # Connect to Neo4j
    driver = GraphDatabase.driver(uri, auth=(username, password))
    
    with driver.session() as session:
        # Cypher query to get all labels and their counts
        query = "CALL db.labels() YIELD label RETURN label, count(*) AS total ORDER BY total DESC"
        result = session.run(query)
        
        # Print results
        for record in result:
            print(f"Label: {record['label']}, Count: {record['total']}")
    
    # Close the driver connection
    driver.close()

def get_index(uri, username, password):
    # Connect to Neo4j
    driver = GraphDatabase.driver(uri, auth=(username, password))
    
    with driver.session() as session:
        # Cypher query to get all labels and their counts
        query = "show indexes"
        result = session.run(query)
        
        # Print results
        for record in result:
            print(record)
    
    # Close the driver connection
    driver.close()


def get_all_nodes(uri, username, password):
    # Connect to Neo4j
    driver = GraphDatabase.driver(uri, auth=(username, password))
    
    with driver.session() as session:
        # Cypher query to get all nodes
        query = "MATCH (n) RETURN COUNT(n) AS total_nodes"
        result = session.run(query)
        
        # Fetch and print the total count of all nodes
        total_nodes = result.single()["total_nodes"]
        print(f"Total Nodes: {total_nodes}")
        
    # Close the driver connection
    driver.close()

def test_pre_filter(uri, username, password):
    # Connect to Neo4j
    driver = GraphDatabase.driver(uri, auth=(username, password))
    
    with driver.session() as session:
        # Cypher query to get all labels and their counts
        query = "MATCH (n) with n CALL db.index.vector.queryNodes('element_embedding_index', 10, $embedding) YIELD node AS element, score RETURN element.id AS id, element.embedding AS embedding, score"
        result = session.run(query)
        
        # Print results
        for record in result:
            print(record)
    
    # Close the driver connection
    driver.close()

# Run the function
get_all_nodes(uri, username, password)

get_index(uri, username, password)

# Run the function
get_node_counts(uri, username, password)
