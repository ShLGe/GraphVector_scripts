import requests
from multiprocessing import Pool, Manager
import time
import json
import numpy as np

ip_list = ["http://10.128.0.16","http://10.128.0.41","http://10.128.0.48","http://10.128.0.52","http://10.128.0.53","http://10.128.0.56","http://10.128.0.57","http://10.128.0.58"]
ip_list_len = len(ip_list)
n_process = 128  # Number of processes to run in parallel

def request_post(url, payload):
    r = requests.post(url, data=json.dumps(payload))
    data = r.json()
    return data

def process_id(id, url, payload):
    query_start_time = time.time_ns()
    response = request_post(url, payload)
    query_end_time = time.time_ns()
    query_latency = (query_end_time - query_start_time) / 1000  # Convert to microseconds
    return id, response, query_latency

def process_in_parallel(id_range, url, payload_list):
    # Create a pool of processes
    with Pool(n_process) as pool:
        results = pool.starmap(process_id, [(id, ip_list[id % ip_list_len] + url, payload_list[i]) for i, id in enumerate(id_range)])
    #ip_list[id % ip_list_len] + 
    # Collect the results into store and latency_store
    store = {}
    latency_store = []
    for id, response, latency in results:
        store[id] = response
        latency_store.append(latency)
    
    return store, latency_store

def calculate_latency_statistics(latencies):
    avg_latency = np.mean(latencies)
    avg_latency_list.append(avg_latency)
    p95_latency = np.percentile(latencies, 95)
    variance = np.var(latencies)
    max_latency = np.max(latencies)
    min_latency = np.min(latencies)
    
    print(f"Average query latency: {avg_latency:.2f} microseconds")
    print(f"95th percentile (P95) latency: {p95_latency:.2f} microseconds")
    print(f"Variance of latencies: {variance:.2f} microseconds squared")
    print(f"Max latency: {max_latency:.2f} microseconds")
    print(f"Min latency: {min_latency:.2f} microseconds")

ef_list = []
recall_list = []
qps_list = []
avg_latency_list = []

def main(k=10, ef_search=32):
    url = ":14240/restpp/query/g1/q1?"  # Adjust the URL if necessary
    query_file = "/home/graphsql/dataset/deep/query.csv"
    groundtruth_file = "/home/graphsql/dataset/deep/deep1000M_groundtruth.csv"
    print("Current concurrency: ", n_process)

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
            "efp": ef_search,
            "embedding": embedding_vector
        }
        payload_list.append(payload)
    end_time = time.time()
    duration_ms = round((end_time - start_time) * 1000, 3)
    print("Query file parsing time:", duration_ms, "ms.")

    # 2. Call the REST API in parallel using process pool
    start_time = time.time()
    results, latencies = process_in_parallel(id_list, url, payload_list)
    end_time = time.time()
    duration_ms = round((end_time - start_time) * 1000, 3)
    print("REST API calling time:", duration_ms, "ms.")
    num_queries = len(id_list)
    qps = num_queries / (end_time - start_time)
    qps_list.append(qps)
    print(f"Queries Per Second (QPS): {qps:.2f}")

    calculate_latency_statistics(latencies)
    print("All query latency record list: ")

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
    for i, id in enumerate(id_list):
        if i < len(results):  # Ensure the index is within bounds
            # Extract the hits for this result
            hits = results[i]['results'][0]['vset']
            # Extract the retrieved IDs from the hits
            retrieved_ids = [hit['v_id'] for hit in hits]
            
            # Compare retrieved IDs with the groundtruth
            for retrieved_id in retrieved_ids:
                if str(int(retrieved_id)-1) in groundtruth[id]:
                    true_positive += 1
    recall = true_positive / len(id_list) / k
    end_time = time.time()
    duration_ms = round((end_time - start_time) * 1000, 3)
    recall_list.append(round(recall * 100, 3))
    print("Recall calculation time:", duration_ms, "ms.")
    print(f"Recall = {recall * 100:.3f}%")
    print("___________________")
    

if __name__ == "__main__":
    for ef in [13, 24, 76, 120, 251]:#, 594, 1200, 2400]:
        #25, 48, 100, 170, 280, 
        time.sleep(1)   
        main(10, ef)
        
    print("EF list is ")
    print(ef_list)
    print("Recall list is ")
    print(recall_list)
    print("QPS list is ")
    print(qps_list)
    print("Latency list is")
    print(avg_latency_list)
