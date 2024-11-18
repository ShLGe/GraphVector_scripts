from neo4j import GraphDatabase
import csv

# Define Neo4j connection details
uri = "bolt://localhost:7687"
username = "neo4j"
password = "lsgneo4j123"

# Connect to the Neo4j database
driver = GraphDatabase.driver(uri, auth=(username, password))

def create_vertex(tx, element_id, embedding):
    tx.run(
        "CREATE (e:Element {id: $element_id, embedding: $embedding})",
        element_id=element_id, embedding=embedding
    )

def load_csv_to_neo4j(csv_file):
    with driver.session() as session:
        with open(csv_file, newline='') as file:
            reader = csv.reader(file)
            for row in reader:
                element_id = row[0]
                embedding = [float(x) for x in row[1:]]  # Convert embedding values to float
                session.write_transaction(create_vertex, element_id, embedding)

# File path to your CSV
csv_file = "/home/graphsql/tigergraph_test/dataset/sift/csv_dataset/sift_base.csv"

# Load CSV data into Neo4j
load_csv_to_neo4j(csv_file)

# Close the Neo4j connection
driver.close()
