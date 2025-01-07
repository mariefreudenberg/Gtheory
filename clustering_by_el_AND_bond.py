"""
# erst bond, dann element clustering
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

# Function to calculate bond order counts
def calculate_bond_order_counts(graph):
    bond_orders = [e[2]['order'] for e in graph.edges(data=True)]
    bond_order_counts = Counter(bond_orders)
    sorted_bond_orders = sorted(bond_order_counts.items())
    bond_order_string = "".join(f"{order}:{count}" for order, count in sorted_bond_orders)
    return bond_order_string

# Function to calculate element counts
def calculate_element_count(graph):
    element_counts = Counter(n['element'] for _, n in graph.nodes(data=True))
    sorted_elements = sorted(element_counts.items())
    element_string = "".join(f"{el}{count}" for el, count in sorted_elements)
    return element_string

# Step 1: Cluster by bond order counts
def cluster_by_bond_order_counts(data):
    clusters = {}
    for i, rc in enumerate(data):
        bond_order_string = calculate_bond_order_counts(rc['reaction_center'])
        if bond_order_string not in clusters:
            clusters[bond_order_string] = []
        clusters[bond_order_string].append(i)
    return list(clusters.values())

# Step 2: Subcluster each bond-based cluster by element counts
def subcluster_by_element_counts(data, bond_clusters):
    final_clusters = []
    for group in bond_clusters:
        element_clusters = {}
        for idx in group:
            element_string = calculate_element_count(data[idx]['reaction_center'])
            if element_string not in element_clusters:
                element_clusters[element_string] = []
            element_clusters[element_string].append(idx)
        final_clusters.extend(list(element_clusters.values()))
    return final_clusters

# Step 3: Post-cluster by isomorphism
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

# Main function
def main():
    # Step 1: Cluster by bond order counts
    start_bond_clustering = time.time()
    bond_clusters = cluster_by_bond_order_counts(data)
    print(f"Bond clusters: {len(bond_clusters)}")
    end_bond_clustering = time.time()

    # Step 2: Subcluster by element counts
    start_element_clustering = time.time()
    element_clusters = subcluster_by_element_counts(data, bond_clusters)
    print(f"Element clusters: {len(element_clusters)}")
    end_element_clustering = time.time()




    # Step 3: Post-cluster by isomorphism
    start_isomorphism_clustering = time.time()
    final_clusters = postcluster_by_isomorphism(data, element_clusters)
    end_isomorphism_clustering = time.time()

    # Timing results
    print(f"Time for clustering by bond orders: {end_bond_clustering - start_bond_clustering:.2f} seconds")
    print(f"Time for subclustering by element counts: {end_element_clustering - start_element_clustering:.2f} seconds")
    print(f"Time for post-clustering by isomorphism: {end_isomorphism_clustering - start_isomorphism_clustering:.2f} seconds")
    print(f"Total time: {end_isomorphism_clustering - start_bond_clustering:.2f} seconds")

    # Final cluster results
    print(f"Number of final clusters: {len(final_clusters)}")

    return final_clusters

# Run the main function
final_clusters = main()
"""

# erst element, dann bond clustering
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
    element_counts = Counter(n['element'] for _, n in graph.nodes(data=True))
    sorted_elements = sorted(element_counts.items())
    element_string = "".join(f"{el}{count}" for el, count in sorted_elements)
    return element_string

# Function to calculate bond order counts
def calculate_bond_order_counts(graph):
    bond_orders = [e[2]['order'] for e in graph.edges(data=True)]
    bond_order_counts = Counter(bond_orders)
    sorted_bond_orders = sorted(bond_order_counts.items())
    bond_order_string = "".join(f"{order}:{count}" for order, count in sorted_bond_orders)
    return bond_order_string

# Step 1: Cluster by element counts
def cluster_by_element_counts(data):
    clusters = {}
    for i, rc in enumerate(data):
        element_string = calculate_element_count(rc['reaction_center'])
        if element_string not in clusters:
            clusters[element_string] = []
        clusters[element_string].append(i)
    return list(clusters.values())

# Step 2: Subcluster each element-based cluster by bond order counts
def subcluster_by_bond_order_counts(data, element_clusters):
    final_clusters = []
    for group in element_clusters:
        bond_clusters = {}
        for idx in group:
            bond_order_string = calculate_bond_order_counts(data[idx]['reaction_center'])
            if bond_order_string not in bond_clusters:
                bond_clusters[bond_order_string] = []
            bond_clusters[bond_order_string].append(idx)
        final_clusters.extend(list(bond_clusters.values()))
    return final_clusters

# Step 3: Post-cluster by isomorphism
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

# Main function
def main():
    # Step 1: Cluster by element counts
    start_element_clustering = time.time()
    element_clusters = cluster_by_element_counts(data)
    print(f"Element clusters: {len(element_clusters)}")
    end_element_clustering = time.time()

    # Step 2: Subcluster by bond order counts
    start_bond_clustering = time.time()
    bond_clusters = subcluster_by_bond_order_counts(data, element_clusters)
    print(f"Bond clusters: {len(bond_clusters)}")
    end_bond_clustering = time.time()

    # Step 3: Post-cluster by isomorphism
    start_isomorphism_clustering = time.time()
    final_clusters = postcluster_by_isomorphism(data, bond_clusters)
    end_isomorphism_clustering = time.time()

    # Timing results
    print(f"Time for clustering by element counts: {end_element_clustering - start_element_clustering:.2f} seconds")
    print(f"Time for subclustering by bond orders: {end_bond_clustering - start_bond_clustering:.2f} seconds")
    print(f"Time for post-clustering by isomorphism: {end_isomorphism_clustering - start_isomorphism_clustering:.2f} seconds")
    print(f"Total time: {end_isomorphism_clustering - start_element_clustering:.2f} seconds")

    # Final cluster results
    print(f"Number of final clusters: {len(final_clusters)}")

    return final_clusters

# Run the main function
final_clusters = main()
