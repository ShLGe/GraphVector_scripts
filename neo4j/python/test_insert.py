from neo4j import GraphDatabase

class Neo4jDatabase:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def insert_node(self, node_label, node_properties):
        with self.driver.session() as session:
            session.write_transaction(self._create_node, node_label, node_properties)

    @staticmethod
    def _create_node(tx, node_label, node_properties):
        query = f"CREATE (n:{node_label} {{"
        query += ', '.join([f"{key}: ${key}" for key in node_properties.keys()])
        query += "})"
        tx.run(query, **node_properties)

if __name__ == "__main__":
    # Replace with your Neo4j credentials
    uri = "bolt://localhost:7687"
    user = "neo4j"
    password = "lsgneo4j123"

    # Create a database connection
    db = Neo4jDatabase(uri, user, password)

    # Define the node label and properties
    label = "Person"
    properties = {"name": "John Doe", "age": 30}

    # Insert the node
    db.insert_node(label, properties)
    print("Node inserted successfully.")

    # Close the database connection
    db.close()
