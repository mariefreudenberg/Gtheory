import pickle
import networkx as nx
import time
from collections import Counter

# Load data
with open('reaction_centers.pkl', 'rb') as f:
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


# Main function to combine both clustering methods and measure time
def main():
    # Step 1: Cluster by element counts
    start_element_clustering = time.time()
    element_clusters = cluster_by_element_counts(data)
    print(len(element_clusters))
    end_element_clustering = time.time()

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
