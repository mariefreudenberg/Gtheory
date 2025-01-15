import pickle
import networkx as nx
import time
from collections import Counter
import matplotlib.pyplot as plt
import math


# Node match function for isomorphism
def node_match(n1, n2):
    return n1['charge'] == n2['charge'] and n1['element'] == n2['element']


# Edge match function for isomorphism
def edge_match(e1, e2):
    return e1['order'] == e2['order']


# Function to calculate element counts
def calculate_element_count(graph):
    element_counts = Counter(n['element'] for _, n in graph.nodes(data=True))
    sorted_elements = sorted(element_counts.items())
    element_string = "".join(f"{el}{count}" for el, count in sorted_elements)
    return element_string


# Function to cluster by element counts
def cluster_by_element_counts(data):
    clusters = {}
    for i, rc in enumerate(data):
        element_string = calculate_element_count(rc['reaction_center'])
        if element_string not in clusters:
            clusters[element_string] = []
        clusters[element_string].append(i)
    return list(clusters.values())


# Function to post-cluster by isomorphism
def postcluster_by_isomorphism(data, element_clusters):
    final_clusters = []
    for group in element_clusters:
        sub_clusters = []
        for idx in group:
            rc = data[idx]['reaction_center']
            is_added = False
            for sub_cluster in sub_clusters:
                representative_rc = data[sub_cluster[0]]['reaction_center']
                if nx.is_isomorphic(rc, representative_rc, node_match=node_match, edge_match=edge_match):
                    sub_cluster.append(idx)
                    is_added = True
                    break
            if not is_added:
                sub_clusters.append([idx])
        final_clusters.extend(sub_clusters)
    return final_clusters


# Function to process a batch
def process_batch(batch_data):
    element_clusters = cluster_by_element_counts(batch_data)
    final_clusters = postcluster_by_isomorphism(batch_data, element_clusters)
    return final_clusters


# Function to split data into chunks
def split_data_into_chunks(data, n):
    chunk_size = math.ceil(len(data) / n)
    return [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]


# Main function to process the dataset in chunks
def main_in_batches(data, n_batches):
    # Split data into n_batches
    chunks = split_data_into_chunks(data, n_batches)
    all_batch_results = []
    times = []

    for batch_idx, chunk in enumerate(chunks):
        print(f"Processing batch {batch_idx + 1}/{n_batches}...")
        start_time = time.time()

        # Process the current chunk
        batch_result = process_batch(chunk)
        all_batch_results.append(batch_result)

        end_time = time.time()
        diff_time = end_time - start_time
        times.append(diff_time)
        print(f"Batch {batch_idx + 1} processed in {diff_time:.2f} seconds.")
        print(f"Number of clusters in batch {batch_idx + 1}: {len(batch_result)}")

    return all_batch_results, times


# Load data
with open('Larger_rcs.pkl', 'rb') as f:
    data = pickle.load(f)

# Run clustering in batches
n_batches = 20  # Adjust the number of batches as needed
results = main_in_batches(data, n_batches)
batch_results = results [0]
all_times = results[1]

# Print the results summary
for i, batch_result in enumerate(batch_results, 1):
    print(f"Batch {i}: {len(batch_result)} clusters")
print(f'list of all times: {all_times}')
