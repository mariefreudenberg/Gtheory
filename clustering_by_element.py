import pickle
import networkx as nx
import time
from collections import Counter

# Load data
with open('Small_RCs_khop_2.pkl', 'rb') as f:
    data = pickle.load(f)


# Node match function for isomorphism
def node_match(n1, n2):
    return n1['charge'] == n2['charge'] and n1['element'] == n2['element']


# Edge match function for isomorphism
def edge_match(e1, e2):
    return e1['order'] == e2['order']


# Function to calculate element counts
def calculate_element_count(graph):
    # Count occurrences of elements in the graph
    element_counts = Counter(n['element'] for _, n in graph.nodes(data=True))
    # Convert to sorted string format (e.g., "C3H2O1")
    sorted_elements = sorted(element_counts.items())
    element_string = "".join(f"{el}{count}" for el, count in sorted_elements)
    return element_string


# Function to cluster by element counts
def cluster_by_element_counts(data):
    clusters = {}

    for i, rc in enumerate(data):
        # Calculate element count string for the current RC
        element_string = calculate_element_count(rc['reaction_center'])

        # Group by element string
        if element_string not in clusters:
            clusters[element_string] = []
        clusters[element_string].append(i)

    return list(clusters.values())  # Return clusters as a list of lists


# Function to post-cluster by isomorphism within each element-based cluster
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

import matplotlib.pyplot as plt

# Function to plot cluster size distribution
def plot_cluster_distribution(clusters):
    # Calculate the size of each cluster
    cluster_sizes = [len(cluster) for cluster in clusters]

    # Create a histogram of cluster sizes
    plt.figure(figsize=(10, 6))
    plt.hist(cluster_sizes, bins=range(1, max(cluster_sizes) + 2), edgecolor='black', align='left')
    plt.xlabel("Cluster Size")
    plt.ylabel("Number of Clusters")
    plt.title("Distribution of Cluster Sizes")
    plt.xticks(range(1, max(cluster_sizes) + 1))
    plt.show()

    # Print summary statistics
    print(f"Total Clusters: {len(clusters)}")
    print(f"Clusters with single molecule graphs: {cluster_sizes.count(1)}")
    print(f"Largest Cluster Size: {max(cluster_sizes)}")

# Main function to combine both clustering methods and measure time
def main():
    # Step 1: Cluster by element counts
    start_element_clustering = time.time()
    element_clusters = cluster_by_element_counts(data)
    print(len(element_clusters))
    end_element_clustering = time.time()

    plot_cluster_distribution(element_clusters)

    # Step 2: Post-cluster by isomorphism
    start_isomorphism_clustering = time.time()
    final_clusters = postcluster_by_isomorphism(data, element_clusters)
    end_isomorphism_clustering = time.time()

    # Total time
    total_time = (end_element_clustering - start_element_clustering) + (
                end_isomorphism_clustering - start_isomorphism_clustering)

    # Output timings
    print(f"Time for clustering by element counts: {end_element_clustering - start_element_clustering:.2f} seconds")
    print(
        f"Time for post-clustering by isomorphism: {end_isomorphism_clustering - start_isomorphism_clustering:.2f} seconds")
    print(f"Total time: {total_time:.2f} seconds")

    # Output results
    print(f"Number of final clusters: {len(final_clusters)}")

    return final_clusters


# Run the main function
final_clusters = main()
