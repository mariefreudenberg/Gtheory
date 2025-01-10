import pickle
import networkx as nx
from networkx.algorithms.graph_hashing import weisfeiler_lehman_graph_hash
import time

# Load data
with open('reaction_centers.pkl', 'rb') as f:
    data = pickle.load(f)


def node_match(n1, n2):
    return n1['charge'] == n2['charge'] and n1['element'] == n2['element']

def edge_match(e1, e2):
    return e1['order'] == e2['order']


# Function to prepare aggregated node attributes
def prepare_node_attributes(graph):
    for node, attrs in graph.nodes(data=True):
        # Combine 'charge' and 'element' into a single string attribute
        attrs['aggregated'] = f"{attrs['element']}_{attrs['charge']}"

# Function to calculate WL graph hash
def calculate_wl_hash(graph):
    # Ensure nodes have aggregated attributes
    prepare_node_attributes(graph)
    # Compute Weisfeiler-Lehman graph hash considering node and edge attributes
    return weisfeiler_lehman_graph_hash(graph, node_attr='aggregated',edge_attr='order',iterations=3) #is order for edges the best option???

# Function to cluster by WL graph hash
def cluster_by_wl_hash(data):
    clusters = {}
    for i, rc in enumerate(data):
        # Calculate WL hash for the current graph
        wl_hash = calculate_wl_hash(rc['reaction_center'])
        # Group by WL hash
        if wl_hash not in clusters:
            clusters[wl_hash] = []
        clusters[wl_hash].append(i)
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

from synutility.SynVis.graph_visualizer import GraphVisualizer
def visualize_top_clusters_representative_graphs(clusters, graphs, algorithm_name, top_n=3):
    # Sort clusters by size in descending order and pick the top N clusters
    sorted_clusters = sorted(clusters, key=len, reverse=True)[:top_n]

    # Set up subplots (1 row per cluster)
    fig, axes = plt.subplots(len(sorted_clusters), 1, figsize=(15, 5 * len(sorted_clusters)))

    # Ensure axes is iterable even if there's only one cluster
    if len(sorted_clusters) == 1:
        axes = [axes]

    # Initialize GraphVisualizer
    vis = GraphVisualizer()

    # Plot representative graphs for the top N clusters
    for rank, (cluster, ax) in enumerate(zip(sorted_clusters, axes), start=1):
        representative_graph = graphs[cluster[0]]  # Choose the first graph as representative
        vis.plot_its(representative_graph, ax, use_edge_color=True)
        ax.set_title(f"Top {rank}: Cluster Representative (Cluster Size: {len(cluster)})\n({algorithm_name})")

    plt.tight_layout()
    plt.show()


# Main function to perform clustering
def main():
    start_invariants = time.time()
    clusters = cluster_by_wl_hash(data)
    print(f"Cluster durch Hash: {len(clusters)}")
    end_invariants = time.time()

    # Step 2: Measure time for post-clustering by isomorphism
    start_isomorphism = time.time()
    final_clusters = postcluster_by_isomorphism(data, clusters)
    end_isomorphism = time.time()

    # Total time
    total_time = (end_invariants - start_invariants) + (end_isomorphism - start_isomorphism)

    print(f"Time for clustering by invariants: {end_invariants - start_invariants:.2f} seconds")
    print(f"Time for post-clustering by isomorphism: {end_isomorphism - start_isomorphism:.2f} seconds")
    print(f"Total time: {total_time:.2f} seconds")

    # Output results
    print(f"Number of final clusters: {len(final_clusters)}")

    #plot_cluster_distribution(final_clusters)
    graphs = [item['reaction_center'] for item in data]
    visualize_top_clusters_representative_graphs(final_clusters, graphs, algorithm_name="WL Clustering", top_n=3)

    return clusters

# Run the main function
clusters = main()
