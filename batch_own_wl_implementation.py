import pickle
import networkx as nx
from collections import Counter, defaultdict
import time
import csv

# Function to split the dataset into batches
def split_dataset(data, num_batches):
    batch_size = len(data) // num_batches
    return [data[i * batch_size: (i + 1) * batch_size] for i in range(num_batches)]

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

# Function to perform WL clustering within a set of graphs
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
    for graph in graphs.values():
        initialize_labels(graph)
    clusters = wl_clustering(graphs, shared_hash_table)
    while True:
        new_clusters = defaultdict(list)
        shared_hash_table = {}
        for cluster_graphs in clusters.values():
            cluster_subgraphs = {idx: graphs[idx] for idx in cluster_graphs}
            sub_clusters = wl_clustering(cluster_subgraphs, shared_hash_table)
            for sub_cluster_key, sub_cluster_graphs in sub_clusters.items():
                new_clusters[sub_cluster_key].extend(sub_cluster_graphs)
        if len(new_clusters) == len(clusters):
            break
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
                if nx.is_isomorphic(rc, representative_rc, node_match=node_match, edge_match=edge_match):
                    sub_cluster.append(idx)
                    is_added = True
                    break
            if not is_added:
                sub_clusters.append([idx])
        final_clusters.extend(sub_clusters)
    return final_clusters

def node_match(n1, n2):
    return n1['charge'] == n2['charge'] and n1['element'] == n2['element']

def edge_match(e1, e2):
    return e1['order'] == e2['order']

# Batch processing function
def process_batch(batch, batch_idx):
    wl_start = time.time()
    final_clusters = recursive_wl_clustering(batch)
    wl_end = time.time()
    wl_time = wl_end - wl_start

    iso_start = time.time()
    post_iso_clusters = postcluster_by_isomorphism(batch, final_clusters)
    iso_end = time.time()
    iso_time = iso_end - iso_start

    total_time = wl_time + iso_time
    print(f"Batch {batch_idx}: WL Time = {wl_time:.2f}s, Isomorphism Time = {iso_time:.2f}s, Total Time = {total_time:.2f}s")
    return {
        "Batch": batch_idx,
        "WL Clusters": len(final_clusters),
        "Isomorphic Clusters": len(post_iso_clusters),
        "WL Time (s)": wl_time,
        "Isomorphism Time (s)": iso_time,
        "Total Time (s)": total_time
    }

# Main function
if __name__ == "__main__":
    with open('Larger_rcs.pkl', 'rb') as f:
        data = pickle.load(f)

    num_batches = 20
    batches = split_dataset(data, num_batches)
    results = []

    for batch_idx, batch in enumerate(batches, start=1):
        result = process_batch(batch, batch_idx)
        results.append(result)

    # Save results to a CSV file
    with open('Large_batch_own_wl_results.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["Batch", "WL Clusters", "Isomorphic Clusters", "WL Time (s)", "Isomorphism Time (s)", "Total Time (s)"])
        writer.writeheader()
        writer.writerows(results)

    print("Batch processing completed. Results saved to 'batch_processing_results.csv'.")
