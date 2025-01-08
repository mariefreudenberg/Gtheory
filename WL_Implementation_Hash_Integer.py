import networkx as nx
import pickle
from collections import Counter, defaultdict


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

    return clusters


# Main function
if __name__ == "__main__":
    # Load data
    with open('reaction_centers.pkl', 'rb') as f:
        data = pickle.load(f)

    # Perform recursive WL clustering
    final_clusters = recursive_wl_clustering(data)

    # Output final results
    print(f"Final number of clusters: {len(final_clusters)}")
