import requests
from threading import Thread
import time
import json
import numpy as np

def request_post(url, payload, username, password):
    headers = {'Content-Type': 'application/json'}
    auth = (username, password)
    r = requests.post(url, headers=headers, data=json.dumps(payload), auth=auth)
    data = r.json()
    return data

def process_id_range(id_range, url, payload_list, username, password, store=None):
    if store is None:
        store = {}
    for i in range(len(id_range)):
        id = id_range[i]
        store[id] = request_post(url, payload_list[i], username, password)
    return store

def threaded_process(n_thread, id_range, url, payload_list, username, password):
    store = {}
    threads = []
    for i in range(n_thread):
        ids = id_range[i::n_thread]
        payloads = payload_list[i::n_thread]
        t = Thread(target=process_id_range, args=(ids, url, payloads, username, password, store))
        threads.append(t)
    [t.start() for t in threads]
    [t.join() for t in threads]
    return store


ef_list = []
recall_list = []
qps_list = []
avg_latency_list = []

def main(k=10, ef_search=32, username="neo4j", password="password"):
    url = "http://127.0.0.1:7474/db/neo4j/tx/commit"  # Adjust the URL if necessary
    query_file = "/home/graphsql/dataset/cohere/cohere_query.csv"
    groundtruth_file = "/home/graphsql/dataset/cohere/cohere10M_groundtruth.csv"
    n_thread = 16
    print("Current concurrency: ", n_thread)

    ef_list.append(ef_search)

    # 1. Query file parsing
    start_time = time.time()
    id_list = []
    payload_list = []
    with open(query_file) as f:
        lines = f.read().splitlines()
    for line in lines:
        splited_line = line.split(",", 1)
        id_list.append(int(splited_line[0]))
        
        # Convert the embedding vector from a comma-separated string to a list of floats
        embedding_vector = [float(x) for x in splited_line[1].split(",")]
        
        payload = {
            "statements": [
                {
                    "statement": f"""
                    CALL db.index.vector.queryNodes('element_embedding_index', {k}, $embedding)
                    YIELD node AS element
                    RETURN element.id AS id
                    """,
                    "parameters": {"embedding": embedding_vector}
                }
            ]
        }
        payload_list.append(payload)
    end_time = time.time()
    duration_ms = round((end_time - start_time) * 1000, 3)
    print("Query file parsing time:", duration_ms, "ms.")

    # 2. Call the REST API in parallel
    start_time = time.time()
    results= threaded_process(n_thread, id_list, url, payload_list, username, password)
    end_time = time.time()
    duration_ms = round((end_time - start_time) * 1000, 3)
    print("REST API calling time:", duration_ms, "ms.")
    num_queries = len(id_list)
    qps = num_queries / (end_time - start_time)
    qps_list.append(qps)
    print(f"Queries Per Second (QPS): {qps:.2f}")


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
            min_heap = results[id]['results'][0]['data']
            for item in min_heap:
                if str(int(item['row'][0])-1) in groundtruth[id]:
                    true_positive += 1
    recall = true_positive / len(id_list) / k
    end_time = time.time()
    duration_ms = round((end_time - start_time) * 1000, 3)
    recall_list.append(round(recall*100, 3))
    print("Recall calculation time:", duration_ms, "ms.")
    print(f"Recall = {recall*100:.3f}%")
    print("___________________")

if __name__ == "__main__":
    for ef in range(10, 20, 10):            
        main(10, ef, username="neo4j", password="lsgneo4j123")
        
    print("EF list is ")
    print(ef_list)
    print("Recall list is ")
    print(recall_list)
    print("QPS list is ")
    print(qps_list)
    print("Latency list is")
    print(avg_latency_list)