import requests
from multiprocessing import Pool, Manager
import time
import json
import numpy as np
from pymilvus import Collection, connections
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
from botocore.session import Session

n_process = 16  # Number of processes to run in parallel

# neptune
NEPTUNE_ENDPOINT = ""
REGION = "us-east-2"
#session = Session()
#credentials = session.get_credentials().get_frozen_credentials()
# neo4j
username = "neo4j"
password = ""
# milvus
connections.connect("default", host="localhost", port="19530")
collection = Collection("Element")

def create_signed_request(url, payload):
    headers = {"Content-Type": "application/json"}
    request = AWSRequest(method="POST", url=url, headers=headers, data=json.dumps(payload))
    SigV4Auth(credentials, "neptune-graph", REGION).add_auth(request)
    return request.prepare()

def simplify_results(results):
    """Simplify Milvus results for serialization."""
    simplified = []
    for result in results:
        simplified.append({
            "id": result.id
        })
    return simplified

def handle_payload(system, url, payload):
    if system == "tigergraph":
        headers = {'GSQL-TIMEOUT': '3600000'}
        r = requests.post(url, headers=headers, data=json.dumps(payload))
        data = r.json()
        return data
    elif system == "neo4j":
        headers = {'Content-Type': 'application/json'}
        auth = (username, password)
        r = requests.post(url, headers=headers, data=json.dumps(payload), auth=auth)
        data = r.json()
        return data
    elif system == "neptune":
        signed_request = create_signed_request(url, payload)
        r = requests.post(
            signed_request.url,
            headers=signed_request.headers,
            data=signed_request.body,
        )
        data = r.json()
        return data
    elif system == "milvus":
        results = collection.search(
            data=payload["emb_vectors"],
            anns_field=payload["search_params"]["anns_field"],
            param={"metric_type": payload["search_params"]["metric_type"], "params": payload["search_params"]["params"]},
            limit=payload["search_params"]["topk"],
            output_fields=payload["search_params"]["output_fields"]
        )
        return [simplify_results(result) for result in results]
    elif system == "milvus_rest":
        headers = {'Content-Type': 'application/json'}
        r = requests.post(url, headers=headers, data=json.dumps(payload))
        data = r.json()
        return data
    else:
        raise ValueError(f"Unsupported system: {system}")



def process_id(system, id, url, payload):
    query_start_time = time.time_ns()
    response = handle_payload(system, url, payload)
    query_end_time = time.time_ns()
    query_latency = (query_end_time - query_start_time) / 1000  # Convert to microseconds
    return id, response, query_latency

def process_in_parallel(system, id_range, url, payload_list):
    # Create a pool of processes
    with Pool(n_process) as pool:
        results = pool.starmap(process_id, [(system, id, url, payload_list[i]) for i, id in enumerate(id_range)])
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

def prepare_url(system):
    if system == "tigergraph":
        return "http://localhost:14240/restpp/query/g1/q1?"
    elif system == "neo4j":
        return "http://127.0.0.1:7474/db/neo4j/tx/commit"
    elif system == "neptune":
        return f"https://{NEPTUNE_ENDPOINT}/queries"
    elif system == "milvus":
        return ""
    elif system == "milvus_rest":
        return "http://localhost:9091/api/v1/search"
    else:
        raise ValueError(f"Unsupported system: {system}")

def prepare_payload(system, ef_search, embedding_vector):
    if system == "tigergraph":
      return {
            "efp": ef_search,
            "embedding": embedding_vector
        }
    elif system == "neo4j":
        return {
              "statements": [
                  {
                      "statement": f"""
                      CALL db.index.vector.queryNodes('element_embedding_index', 10 , $embedding)
                      YIELD node AS element
                      RETURN element.id AS id
                      """,
                      "parameters": {"embedding": embedding_vector}
                  }
              ]
        }
    elif system == "neptune":
        return  {
            "queryLanguage": "openCypher",
            "query": f"""
            CALL neptune.algo.vectors.topKByEmbedding({embedding_vector}, {{topK: 10}}) YIELD node
            RETURN node
            """,
        }
    elif system == "milvus":
        return {
          #"collection_name": "Element",
          "emb_vectors": [embedding_vector],
          "search_params": {
              "anns_field": "vector",  # The name of the field that stores your vector embeddings
              "topk": 10,
              "params": {"ef": ef_search},
              "metric_type": "L2",  # Adjust according to your use case
              "output_fields": ["id"]
          }
        }
    elif system == "milvus_rest":
        return {
            "collection_name": "Element",  # Adjust with your Milvus collection name
            "output_fields": ["id"],  # Replace with your desired output fields
            "search_params": [
                {"key": "anns_field", "value": "vector"},  # Adjust your field name
                {"key": "topk", "value": str(10)},
                {"key": "params", "value": "{\"ef\": " + str(ef_search) + "}"},
                {"key": "metric_type", "value": "L2"}  # Adjust metric if necessary
            ],
            "vectors": [embedding_vector],
            "dsl_type": 1
        }
    else:
        raise ValueError(f"Unsupported system: {system}")

def extract_id(system, result):
    if system == "tigergraph":
        hits = result['results'][0]['vset']
        # Extract the retrieved IDs from the hits
        return [hit['v_id'] for hit in hits]
    elif system == "neo4j":
        hits = result['results'][0]['data']
        return [hit['row'][0] for hit in hits]
    elif system == "neptune":
        return [
            result["node"]["~id"] for result in result.get("results", [])
        ]
    elif system == "milvus":
        hits = result[0]
        return [hit['id'] for hit in hits]
    elif system == "milvus_rest":
        return results["results"]["ids"]["IdField"]["IntId"]["data"]

def main(k=10, ef_search=32, system="tigergraph"):
    url = prepare_url(system)
    query_file = "/home/graphsql/dataset/deep/deep_query.csv"
    groundtruth_file = "/home/graphsql/dataset/deep/deep100M_groundtruth.csv"
    print("Current concurrency: ", n_process)
    print("Current ef: ", ef_search)

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
        
        payload = prepare_payload(system, ef_search, embedding_vector)
        payload_list.append(payload)
    end_time = time.time()
    duration_ms = round((end_time - start_time) * 1000, 3)
    print("Query file parsing time:", duration_ms, "ms.")

    # 2. Call the REST API in parallel using process pool
    start_time = time.time()
    results, latencies = process_in_parallel(system, id_list, url, payload_list)
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
            retrieved_ids = extract_id(system, results[i])
            # Compare retrieved IDs with the groundtruth
            for retrieved_id in retrieved_ids:
                if str(int(retrieved_id)) in groundtruth[i]:
                    true_positive += 1
    recall = true_positive / len(id_list) / k
    end_time = time.time()
    duration_ms = round((end_time - start_time) * 1000, 3)
    recall_list.append(round(recall * 100, 3))
    print("Recall calculation time:", duration_ms, "ms.")
    print(f"Recall = {recall * 100:.3f}%")
    print("___________________")
    

if __name__ == "__main__":
    system = "milvus"
    for ef in [12, 22, 74, 126, 257]:#, 594, 1200, 2400]:
        #25, 48, 100, 170, 280, 
        time.sleep(1)   
        main(10, ef, system)
        
    print("EF list is ")
    print(ef_list)
    print("Recall list is ")
    print(recall_list)
    print("QPS list is ")
    print(qps_list)
    print("Latency list is")
    print(avg_latency_list)
