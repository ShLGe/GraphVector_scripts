from neo4j import GraphDatabase
import time

# Define Neo4j connection details
uri = "bolt://localhost:7687"
username = "neo4j"
password = "lsgneo4j123"

# Connect to the Neo4j database
driver = GraphDatabase.driver(uri, auth=(username, password))

def load_csv_data():
    # Cypher query to load CSV data into Neo4j
    query = """
    LOAD CSV FROM 'file:///dataset/bigann/bigann1M_base.csv' AS row
    MERGE (:Element {
        id: toInteger(row[0]), 
        embedding: toFloatList(split(row[1], ':'))
    })
    """

    with driver.session() as session:
        session.run(query)

# Call the function to load CSV data
start_time = time.time_ns()
load_csv_data()
end_time = time.time_ns()

# Calculate and print the total time taken in microseconds
total_time_microseconds = (end_time - start_time) / 1000
print(f"Time taken to insert: {total_time_microseconds} microseconds")

# Close the Neo4j connection
driver.close()
