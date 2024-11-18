import requests
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
from botocore.session import Session
from multiprocessing import Pool
import json
import time
import numpy as np

# Neptune Configuration
NEPTUNE_ENDPOINT = "g-g7vdaoqak6.us-east-2.neptune-graph.amazonaws.com"
REGION = "us-east-2"
n_process = 16

# AWS Credentials
session = Session()
credentials = session.get_credentials().get_frozen_credentials()

# Create SigV4-signed request
def create_signed_request(endpoint, region, payload):
    url = f"https://{endpoint}/queries"
    headers = {"Content-Type": "application/json"}
    request = AWSRequest(method="POST", url=url, headers=headers, data=payload)
    SigV4Auth(credentials, "neptune-graph", region).add_auth(request)
    return request.prepare()

# Send vector search query
def send_vector_search_query(vector):
    payload = {
        "queryLanguage": "openCypher",
        "query": f"""
        CALL neptune.algo.vectors.topKByEmbedding({vector}, {{topK: 10}}) YIELD node
        RETURN node
        """,
    }
    payload_str = json.dumps(payload)
    signed_request = create_signed_request(NEPTUNE_ENDPOINT, REGION, payload_str)
    response = requests.post(
        signed_request.url,
        headers=signed_request.headers,
        data=signed_request.body,
    )
    return response.json()

# Query execution function
def execute_query(id, vector, top_k):
    query_start_time = time.time_ns()
    response = send_vector_search_query(vector)
    query_end_time = time.time_ns()
    latency = (query_end_time - query_start_time) / 1000  # Convert to microseconds
    return id, response, latency

# Parallel query processing
def process_in_parallel(id_range, vector_list, top_k):
    with Pool(n_process) as pool:
        results = pool.starmap(
            execute_query,
            [(id, vector_list[id], top_k) for id in id_range],
        )
    store = {}
    latency_store = []
    for id, response, latency in results:
        store[id] = response
        latency_store.append(latency)
    return store, latency_store

# Latency statistics calculation
def calculate_latency_statistics(latencies):
    avg_latency = np.mean(latencies)
    p95_latency = np.percentile(latencies, 95)
    variance = np.var(latencies)
    max_latency = np.max(latencies)
    min_latency = np.min(latencies)
    print(f"Average latency: {avg_latency:.2f} µs")
    print(f"P95 latency: {p95_latency:.2f} µs")
    print(f"Variance: {variance:.2f} µs^2")
    print(f"Max latency: {max_latency:.2f} µs")
    print(f"Min latency: {min_latency:.2f} µs")

def extract_retrieved_ids(response_json):
    try:
        return [
            result["node"]["~id"] for result in response_json.get("results", [])
        ]
    except KeyError:
        print("Error: Invalid response structure.")
        return []

# Main function
def main():
    query_file = "/home/graphsql/dataset/spacev/spacev_query.csv"
    groundtruth_file = "/home/graphsql/dataset/spacev/spacev100M_groundtruth.csv"
    top_k = 10

    # Parse query file
    print("Parsing query file...")
    id_list = []
    vector_list = []
    with open(query_file) as f:
        lines = f.read().splitlines()
    
    for line in lines:
        parts = line.split(",", 1)
        id_list.append(int(parts[0]))
        vector_list.append([float(x) for x in parts[1].split(",")])

    # Process queries in parallel
    print("Executing queries in parallel...")
    start_time = time.time()
    results, latencies = process_in_parallel(id_list, vector_list, top_k)
    end_time = time.time()
    duration = end_time - start_time
    qps = len(id_list) / duration
    print(f"QPS: {qps:.2f}")

    calculate_latency_statistics(latencies)

    # Extract retrieved node IDs from the response

    # Calculate recall
    print("Calculating recall...")
    groundtruth = {}
    with open(groundtruth_file, "r") as f:
        for line in f:
            parts = line.split(",", top_k + 1)
            groundtruth[int(parts[0])] = [int(x) for x in parts[1:top_k + 1]]

    true_positives = 0
    for id in id_list:
        retrieved_ids = extract_retrieved_ids(results[id])
        true_positives += sum(
            1 for rid in retrieved_ids if int(rid)-1 in groundtruth.get(id, [])
        )

    recall = true_positives / (len(id_list) * top_k)
    print(f"Recall: {recall:.2%}")

if __name__ == "__main__":
    main()
