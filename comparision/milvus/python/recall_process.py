from pymilvus import Collection, connections
import numpy as np
import time
from multiprocessing import Pool, Manager
import json

connections.connect("default", host="localhost", port="19530")
collection = Collection("Element")

def simplify_results(results):
    """Simplify Milvus results for serialization."""
    simplified = []
    for result in results:
        simplified.append({
            "id": result.id,
            "distance": result.distance
        })
    return simplified

def process_id(id, collection_name, vectors, search_params):
    query_start_time = time.time_ns()
      # Get an existing collection
    vector = [vectors]
    results = collection.search(
            data=vector,
            anns_field=search_params["anns_field"],
            param={"metric_type": search_params["metric_type"], "params": search_params["params"]},
            limit=search_params["topk"],
            output_fields=search_params["output_fields"]
        )
    query_end_time = time.time_ns()
    query_latency = (query_end_time - query_start_time) / 1000  # Convert to microseconds
    simplified_results = [simplify_results(result) for result in results]
    return id, simplified_results, query_latency


def multiprocess_search(n_processes, id_range, vectors, collection_name, search_params):
    # Create a pool of processes
    with Pool(n_processes) as pool:
        results = pool.starmap(process_id, [(id, collection_name, vectors[i], search_params) for i, id in enumerate(id_range)])
    #ip_list[id % ip_list_len] + 
    # Collect the results into store and latency_store
    store = {}
    latency_store = []
    for id, results, latency in results:
        store[id] = results
        latency_store.append(latency)
    
    return store, latency_store


ef_list = []
recall_list = []
qps_list = []
avg_latency_list = []


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


def main(collection_name="Element", k=10, ef_search=11):
    print("Current ef: ", ef_search)
    ef_list.append(ef_search)
    query_file = "/home/graphsql/dataset/spacev/spacev_query.csv"
    groundtruth_file = "/home/graphsql/dataset/spacev/spacev100M_groundtruth.csv"
    n_processes = 16  # Number of processes
    print("Current concurrency (processes): ", n_processes)

    # Connect to Milvus

    search_params = {
        "anns_field": "vector",  # The name of the field that stores your vector embeddings
        "topk": k,
        "params": {"ef": ef_search},
        "metric_type": "L2",  # Adjust according to your use case
        "output_fields": ["id"]
    }

    # 1. Query file parsing
    start_time = time.time()
    id_list = []
    vectors = []
    with open(query_file) as f:
        lines = f.read().splitlines()
    for line in lines:
        splited_line = line.split(",", 1)
        id_list.append(int(splited_line[0]))

        # Convert the embedding vector from a comma-separated string to a list of floats
        embedding_vector = np.array([float(x) for x in splited_line[1].split(",")]).tolist()
        vectors.append(embedding_vector)
    end_time = time.time()
    duration_ms = round((end_time - start_time) * 1000, 3)
    print("Query file parsing time:", duration_ms, "ms.")

    # 2. Search in Milvus in parallel using multiprocessing
    start_time = time.time()
    results, latencies = multiprocess_search(n_processes, id_list, vectors, collection_name, search_params)
    end_time = time.time()
    duration_ms = round((end_time - start_time) * 1000, 3)
    print("Milvus search time:", duration_ms, "ms.")
    num_queries = len(id_list)
    qps = num_queries / (end_time - start_time)
    qps_list.append(qps)
    print(f"Queries Per Second (QPS): {qps:.2f}")
    
    # Log each query's latency and calculate statistics
    calculate_latency_statistics(latencies)
    print("All query latency record list: ")
    #print(latencies)

    # 3. Groundtruth file parsing
    start_time = time.time()
    groundtruth = {}
    with open(groundtruth_file) as f:
        lines = f.read().splitlines()
    for line in lines:
        splited_line = line.split(",", k + 1)
        groundtruth[int(splited_line[0])] = splited_line[1:k + 1]
    end_time = time.time()
    duration_ms = round((end_time - start_time) * 1000, 3)
    print("Groundtruth file parsing time:", duration_ms, "ms.")

    # 4. Calculate the recall
    start_time = time.time()
    true_positive = 0
    for i, id in enumerate(id_list):
        if i < len(results):  # Ensure the index is within bounds
            # Extract the hits for this result
            hits = results[i][0]
            
            # Extract the retrieved IDs from the hits
            retrieved_ids = [hit['id'] for hit in hits]
            
            # Compare retrieved IDs with the groundtruth
            for retrieved_id in retrieved_ids:
                if str(int(retrieved_id)) in groundtruth[id]:
                    true_positive += 1

    # Calculate recall
    recall = true_positive / (len(id_list) * k)
    end_time = time.time()
    duration_ms = round((end_time - start_time) * 1000, 3)

    print("Recall calculation time:", duration_ms, "ms.")
    print(f"Recall = {recall * 100:.3f}%")
    recall_list.append(recall * 100)
    print("___________________")


if __name__ == "__main__":
    for ef in [10]:#, 15, 25, 50, 150, 625]:  # Range of ef_search values
        main("Element", 10, ef)

    print("EF list is ")
    print(ef_list)
    print("Recall list is ")
    print(recall_list)
    print("QPS list is ")
    print(qps_list)
    print("Latency list is")
    print(avg_latency_list)
