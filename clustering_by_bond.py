import pickle
import networkx as nx
from collections import Counter
import time

# Load data
with open('reaction_centers.pkl', 'rb') as f:
    data = pickle.load(f)


# Function to calculate bond order counts
def calculate_bond_order_counts(graph):
    # Extract bond orders (tuples) for all edges
    bond_orders = [e[2]['order'] for e in graph.edges(data=True)]
    # Count occurrences of each bond order tuple
    bond_order_counts = Counter(bond_orders)
    # Convert to sorted string format for consistent representation
    sorted_bond_orders = sorted(bond_order_counts.items())
    bond_order_string = "".join(f"{order}:{count}" for order, count in sorted_bond_orders)
    return bond_order_string


# Function to cluster by bond order counts
def cluster_by_bond_order_counts(data):
    clusters = {}

    for i, rc in enumerate(data):
        # Calculate bond order string for the current RC
        bond_order_string = calculate_bond_order_counts(rc['reaction_center'])

        # Group by bond order string
        if bond_order_string not in clusters:
            clusters[bond_order_string] = []
        clusters[bond_order_string].append(i)

    return list(clusters.values())  # Return clusters as a list of lists


# Main function to combine both clustering methods and measure time
def main():

    # Step 1: Cluster by bond order counts
    start_bond_clustering = time.time()
    bond_clusters = cluster_by_bond_order_counts(data)
    print(len(bond_clusters))
    end_bond_clustering = time.time()

    # Step 2: Post-cluster by isomorphism within each bond-based cluster
    start_isomorphism_clustering = time.time()
    final_clusters = postcluster_by_isomorphism(data, bond_clusters)
    end_isomorphism_clustering = time.time()

    # Total time
    total_time = (end_bond_clustering - start_bond_clustering) + (
                end_isomorphism_clustering - start_isomorphism_clustering)

    # Output timings
    print(f"Time for clustering by bond orders: {end_bond_clustering - start_bond_clustering:.2f} seconds")
    print(
        f"Time for post-clustering by isomorphism: {end_isomorphism_clustering - start_isomorphism_clustering:.2f} seconds")
    print(f"Total time: {total_time:.2f} seconds")

    # Output results
    print(f"Number of final clusters: {len(final_clusters)}")

    return final_clusters


# Function for post-clustering by isomorphism (same as before)
def postcluster_by_isomorphism(data, bond_clusters):
    final_clusters = []

    for group in bond_clusters:
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


# Node and edge match functions for isomorphism
def node_match(n1, n2):
    return n1['charge'] == n2['charge'] and n1['element'] == n2['element']


def edge_match(e1, e2):
    return e1['order'] == e2['order']


# Run the main function
final_clusters = main()
