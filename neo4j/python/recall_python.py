from neo4j import GraphDatabase
from threading import Thread
import time

# Neo4j connection class
class Neo4jConnector:
    def __init__(self, uri, username, password):
        self.driver = GraphDatabase.driver(uri, auth=(username, password))

    def close(self):
        self.driver.close()

    def query(self, cypher_query, parameters=None):
        with self.driver.session() as session:
            result = session.run(cypher_query, parameters)
            return result.data()

def process_id_range(id_range, connector, query_list, store=None):
    if store is None:
        store = {}
    for i in range(len(id_range)):
        id = id_range[i]
        query = query_list[i]['query']
        parameters = query_list[i].get('parameters', {})
        store[id] = connector.query(query, parameters)
    return store

def threaded_process(n_thread, id_range, connector, query_list):
    store = {}
    threads = []
    for i in range(n_thread):
        ids = id_range[i::n_thread]
        queries = query_list[i::n_thread]
        t = Thread(target=process_id_range, args=(ids, connector, queries, store))
        threads.append(t)
    [t.start() for t in threads]
    [t.join() for t in threads]
    return store

ef_list = []
batch_search_time = []
single_search_time = []
recall_list = []

def main(k=10, ef_search=32, uri="bolt://localhost:7687", username="neo4j", password="password"):
    connector = Neo4jConnector(uri, username, password)
    
    query_file = "/home/graphsql/dataset/bigann/bigann_query.csv"
    groundtruth_file = "/home/graphsql/dataset/bigann/bigann1M_groundtruth.csv"
    n_thread = 8

    ef_list.append(ef_search)

    # 1. Query file parsing
    start_time = time.time()
    id_list = []
    query_list = []
    with open(query_file) as f:
        lines = f.read().splitlines()
    for line in lines:
        splited_line = line.split(",", 1)
        id_list.append(int(splited_line[0]))
        
        # Convert the embedding vector from a comma-separated string to a list of floats
        embedding_vector = [float(x) for x in splited_line[1].split(",")]
        
        query = f"""
        CALL db.index.vector.queryNodes('element_embedding_index', {k}, $embedding)
        YIELD node AS element, score
        RETURN element.id AS id, element.embedding AS embedding, score
        """
        
        query_list.append({"query": query, "parameters": {"embedding": embedding_vector}})
    end_time = time.time()
    duration_ms = round((end_time - start_time) * 1000, 3)
    print("Query file parsing time:", duration_ms, "ms.")

    # 2. Execute the queries in parallel
    start_time = time.time()
    results = threaded_process(n_thread, id_list, connector, query_list)
    end_time = time.time()
    duration_ms = round((end_time - start_time) * 1000, 3)
    print("Query execution time:", duration_ms, "ms.")

    # 3. Groundtruth file parsing
    start_time = time.time()
    with open(groundtruth_file) as f:
        lines = f.read().splitlines()
    groundtruth = {}
    end_col = k + 1
    for line in lines:
        splited_line = line.split(",", end_col)
        groundtruth[int(splited_line[0])] = splited_line[1:end_col]
    end_time = time.time()
    duration_ms = round((end_time - start_time) * 1000, 3)
    print("Groundtruth file parsing time:", duration_ms, "ms.")

    # 4. Calculate the recall
    start_time = time.time()
    true_positive = 0
    for id in id_list:
        if id in results:
            retrieved_ids = [record['id'] for record in results[id]]
            for retrieved_id in retrieved_ids:
                if str(int(retrieved_id)-1) in groundtruth[id]:
                    true_positive += 1
    recall = true_positive / len(id_list) / k
    end_time = time.time()
    duration_ms = round((end_time - start_time) * 1000, 3)
    recall_list.append(round(recall * 100, 3))
    print("Recall calculation time:", duration_ms, "ms.")
    print(f"Recall = {recall * 100:.3f}%")

    connector.close()

if __name__ == "__main__":
    for ef in range(10, 20, 10):
        main(10, ef, uri="bolt://localhost:7687", username="neo4j", password="")
        
    print("ef list is ")
    print(ef_list)
    print("Batch search time is ")
    print(batch_search_time)
    print("Single search time is ")
    print(single_search_time)
    print("Recall list is ")
    print(recall_list)
