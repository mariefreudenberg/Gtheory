import networkx as nx
import pickle
from collections import Counter, defaultdict
import time

# Function to initialize node labels WITH edge labels
def initialize_labels(graph):
    for node, attrs in graph.nodes(data=True):
        # Combine 'element' and 'charge' as the base label
        base_label = f"{attrs['element']}_{attrs['charge']}"

        # Collect 'order' attributes from edges connected to the current node
        neighbor_edge_orders = sorted([str(graph[node][neighbor]['order']) for neighbor in graph.neighbors(node)])


        # Combine the base label with the sorted edge 'order' attributes
        attrs['label'] = f"{base_label},{','.join(neighbor_edge_orders)}"


# Function to perform a single Weisfeiler-Lehman iteration using a shared hash table
def wl_iteration_with_shared_hash(graph, shared_hash_table):
    new_labels = {}
    for node, attrs in graph.nodes(data=True):
        # Get current label and sorted labels of neighbors
        current_label = attrs['label']
        #neighbor_labels = sorted([graph.nodes[neighbor]['label'] for neighbor in graph.neighbors(node)])

        neighbor_labels = sorted([
            f"{graph.nodes[neighbor]['label']}_{graph[node][neighbor]['order']}"
            for neighbor in graph.neighbors(node)
        ])

        # Create new label as a combination of current and neighbor labels
        aggregated_label = f"{current_label},{','.join(neighbor_labels)}"
        # Compute the real integer hash of the aggregated label using a shared hash table
        if aggregated_label not in shared_hash_table:
            shared_hash_table[aggregated_label] = len(shared_hash_table)
        new_labels[node] = shared_hash_table[aggregated_label]
    # Update labels in the graph
    for node, new_label in new_labels.items():
        graph.nodes[node]['label'] = str(new_label)  # Store the integer hash as a string for consistency


# Function to generate histogram of labels
def generate_histogram(graph):
    # Collect the current labels of all nodes
    labels = [attrs['label'] for _, attrs in graph.nodes(data=True)]
    # Count occurrences of each label
    histogram = Counter(labels)
    return histogram


# Function to perform WL clustering within a set of graphs
def wl_clustering(graphs, shared_hash_table):
    graph_histograms = {}

    # Perform WL iteration and generate histograms for each graph
    for graph_idx, graph in graphs.items():
        wl_iteration_with_shared_hash(graph, shared_hash_table)  # Perform WL iteration
        histogram = generate_histogram(graph)  # Generate histogram
        graph_histograms[graph_idx] = histogram

    # Cluster graphs by their histograms
    clusters = defaultdict(list)
    for graph_idx, histogram in graph_histograms.items():
        histogram_tuple = tuple(sorted(histogram.items()))  # Convert histogram to a hashable tuple
        clusters[histogram_tuple].append(graph_idx)

    return clusters


# Function to perform recursive WL clustering
def recursive_wl_clustering(data):
    # Initialize shared hash table
    shared_hash_table = {}

    # Initialize clusters with all graphs
    clusters = defaultdict(list)
    graphs = {i: item['reaction_center'] for i, item in enumerate(data)}

    # Initial clustering by first WL iteration
    for graph_idx, graph in graphs.items():
        initialize_labels(graph)  # Initialize labels
    clusters = wl_clustering(graphs, shared_hash_table)  # First WL clustering

    num_clusters = len(clusters)
    iteration = 1
    print(f"Iteration {iteration}: Number of clusters = {num_clusters}")

    # Perform recursive WL clustering
    while True:
        new_clusters = defaultdict(list)
        shared_hash_table = {}  # Reset shared hash table for each iteration

        # Process each cluster independently
        for cluster_graphs in clusters.values():
            cluster_subgraphs = {idx: graphs[idx] for idx in cluster_graphs}
            sub_clusters = wl_clustering(cluster_subgraphs, shared_hash_table)
            for sub_cluster_key, sub_cluster_graphs in sub_clusters.items():
                new_clusters[sub_cluster_key].extend(sub_cluster_graphs)

        iteration += 1
        num_new_clusters = len(new_clusters)
        print(f"Iteration {iteration}: Number of clusters = {num_new_clusters}")

        # Check if the number of clusters has stabilized
        if num_new_clusters == num_clusters:
            break
        num_clusters = num_new_clusters
        clusters = new_clusters

    return list(clusters.values())

def node_match(n1, n2):
    return n1['charge'] == n2['charge'] and n1['element'] == n2['element']

def edge_match(e1, e2):
    return e1['order'] == e2['order']

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


import matplotlib.pyplot as plt


# Function to plot cluster size distribution
def plot_cluster_distribution(clusters):
    # Calculate the size of each cluster
    cluster_sizes = [len(cluster) for cluster in clusters]

    # Count the frequency of each cluster size
    size_counts = Counter(cluster_sizes)

    # Sort the sizes and their counts
    sizes = sorted(size_counts.keys())
    counts = [size_counts[size] for size in sizes]

    # Create a bar plot for the cluster size distribution
    plt.figure(figsize=(10, 6))
    plt.bar(sizes, counts, width=0.8, edgecolor='black', align='center')
    plt.xlabel("Cluster Size")
    plt.ylabel("Number of Clusters")
    plt.title("Distribution of Cluster Sizes")
    plt.xticks(sizes)  # Only include sizes that are present
    plt.show()

    # Print summary statistics
    print(f"Total Clusters: {len(clusters)}")
    print(f"Clusters with single molecule graphs: {size_counts.get(1, 0)}")
    print(f"Largest Cluster Size: {max(cluster_sizes)}")


# Main function
if __name__ == "__main__":
    # Load data
    with open('Small_RCs_khop_2.pkl', 'rb') as f:
        data = pickle.load(f)
    wl_start = time.time()
    # Perform recursive WL clustering
    final_clusters = recursive_wl_clustering(data)
    wl_end = time.time()
    wl_time = wl_end - wl_start
    print(f"Time for WL-Implementation: {wl_time:.2f}s")

    iso_start = time.time()
    post_iso_clusters = postcluster_by_isomorphism(data,final_clusters)
    iso_end = time.time()

    iso_time = iso_end - iso_start
    print(f"Time for Post Clustering Isomorphism Test: {iso_time:.2f}s")

    # Output final results
    print(f"Final number of clusters after WL Test: {len(final_clusters)}")
    print(f"Final number of clusters after classy Isomorphism Test: {len(post_iso_clusters)}")

    print(f"Time in total: {wl_time + iso_time:.2f}s")

    plot_cluster_distribution(final_clusters)
