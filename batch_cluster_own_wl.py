import networkx as nx
import pickle
from collections import Counter, defaultdict
import time
import math


# Function to initialize node labels WITH edge labels
def initialize_labels(graph):
    for node, attrs in graph.nodes(data=True):
        base_label = f"{attrs['element']}_{attrs['charge']}"
        neighbor_edge_orders = sorted([str(graph[node][neighbor]['order']) for neighbor in graph.neighbors(node)])
        attrs['label'] = f"{base_label},{','.join(neighbor_edge_orders)}"


# Function to perform a single Weisfeiler-Lehman iteration using a shared hash table
def wl_iteration_with_shared_hash(graph, shared_hash_table):
    new_labels = {}
    for node, attrs in graph.nodes(data=True):
        current_label = attrs['label']
        neighbor_labels = sorted([
            f"{graph.nodes[neighbor]['label']}_{graph[node][neighbor]['order']}"
            for neighbor in graph.neighbors(node)
        ])
        aggregated_label = f"{current_label},{','.join(neighbor_labels)}"
        if aggregated_label not in shared_hash_table:
            shared_hash_table[aggregated_label] = len(shared_hash_table)
        new_labels[node] = shared_hash_table[aggregated_label]
    for node, new_label in new_labels.items():
        graph.nodes[node]['label'] = str(new_label)


# Function to generate histogram of labels
def generate_histogram(graph):
    labels = [attrs['label'] for _, attrs in graph.nodes(data=True)]
    histogram = Counter(labels)
    return histogram


# Function to perform WL clustering
def wl_clustering(graphs, shared_hash_table):
    graph_histograms = {}
    for graph_idx, graph in graphs.items():
        wl_iteration_with_shared_hash(graph, shared_hash_table)
        histogram = generate_histogram(graph)
        graph_histograms[graph_idx] = histogram
    clusters = defaultdict(list)
    for graph_idx, histogram in graph_histograms.items():
        histogram_tuple = tuple(sorted(histogram.items()))
        clusters[histogram_tuple].append(graph_idx)
    return clusters


# Function to perform recursive WL clustering
def recursive_wl_clustering(data):
    shared_hash_table = {}
    clusters = defaultdict(list)
    graphs = {i: item['reaction_center'] for i, item in enumerate(data)}
    for graph_idx, graph in graphs.items():
        initialize_labels(graph)
    clusters = wl_clustering(graphs, shared_hash_table)
    num_clusters = len(clusters)
    iteration = 1
    print(f"Iteration {iteration}: Number of clusters = {num_clusters}")
    while True:
        new_clusters = defaultdict(list)
        shared_hash_table = {}
        for cluster_graphs in clusters.values():
            cluster_subgraphs = {idx: graphs[idx] for idx in cluster_graphs}
            sub_clusters = wl_clustering(cluster_subgraphs, shared_hash_table)
            for sub_cluster_key, sub_cluster_graphs in sub_clusters.items():
                new_clusters[sub_cluster_key].extend(sub_cluster_graphs)
        iteration += 1
        num_new_clusters = len(new_clusters)
        print(f"Iteration {iteration}: Number of clusters = {num_new_clusters}")
        if num_new_clusters == num_clusters:
            break
        num_clusters = num_new_clusters
        clusters = new_clusters
    return list(clusters.values())


# Function to post-cluster by isomorphism
def postcluster_by_isomorphism(data, invariant_clusters):
    final_clusters = []
    for group in invariant_clusters:
        sub_clusters = []
        for idx in group:
            rc = data[idx]['reaction_center']
            is_added = False
            for sub_cluster in sub_clusters:
                representative_rc = data[sub_cluster[0]]['reaction_center']
                if nx.is_isomorphic(rc, representative_rc, node_match=lambda n1, n2: n1['charge'] == n2['charge'] and n1['element'] == n2['element'], edge_match=lambda e1, e2: e1['order'] == e2['order']):
                    sub_cluster.append(idx)
                    is_added = True
                    break
            if not is_added:
                sub_clusters.append([idx])
        final_clusters.extend(sub_clusters)
    return final_clusters


# Function to split data into chunks
def split_data_into_chunks(data, n_batches):
    chunk_size = math.ceil(len(data) / n_batches)
    return [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]


# Main function to process in batches
def main_in_batches(data, n_batches):
    chunks = split_data_into_chunks(data, n_batches)
    batch_results = []
    batch_times = []

    for batch_idx, chunk in enumerate(chunks):
        print(f"Processing batch {batch_idx + 1}/{n_batches}...")
        start_time = time.time()

        # Perform WL clustering on the current batch
        initial_clusters = recursive_wl_clustering(chunk)
        final_clusters = postcluster_by_isomorphism(chunk, initial_clusters)

        end_time = time.time()
        batch_time = end_time - start_time

        batch_results.append(final_clusters)
        batch_times.append(batch_time)

        print(f"Batch {batch_idx + 1} processed in {batch_time:.2f} seconds.")
        print(f"Initial clusters: {len(initial_clusters)}, Final clusters: {len(final_clusters)}")

    return batch_results, batch_times


# Load data
with open('reaction_centers.pkl', 'rb') as f:
    data = pickle.load(f)

# Process data in batches
n_batches = 20  # Adjust the number of batches as needed
results, runtimes = main_in_batches(data, n_batches)

# Output batch results
for batch_idx, clusters in enumerate(results, 1):
    print(f"Batch {batch_idx}: {len(clusters)} clusters")

print(f"Runtimes for each batch: {runtimes}")
