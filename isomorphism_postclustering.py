import pickle
import networkx as nx
import time

# Load data
with open('reaction_centers.pkl', 'rb') as f:
    data = pickle.load(f)

# Node match function
def node_match(n1, n2):
    return n1['charge'] == n2['charge'] and n1['element'] == n2['element']

# Edge match function
def edge_match(e1, e2):
    return e1['order'] == e2['order']

# Function to calculate invariants
def calculate_invariants(graph):
    degrees = sorted(dict(graph.degree()).values())
    #density = nx.density(graph)
    #avg_shortest_path = nx.average_shortest_path_length(graph) if nx.is_connected(graph) else None
    return (degrees)    #, density, avg_shortest_path)

# Function to cluster by invariants
def cluster_by_invariants(data):
    clusters = []
    invariants_per_group = []

    for i, rc in enumerate(data):
        invariants = calculate_invariants(rc['reaction_center'])
        is_added = False
        for group_idx, group_invariants in enumerate(invariants_per_group):
            if invariants == group_invariants:
                clusters[group_idx].append(i)
                is_added = True
                break
        if not is_added:
            clusters.append([i])
            invariants_per_group.append(invariants)

    return clusters

# Function to post-cluster by isomorphism within each invariant group
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

# Main function to combine both clustering methods and measure time
def main():
    # Step 1: Measure time for clustering by invariants
    start_invariants = time.time()
    invariant_clusters = cluster_by_invariants(data)
    end_invariants = time.time()

    # Step 2: Measure time for post-clustering by isomorphism
    start_isomorphism = time.time()
    final_clusters = postcluster_by_isomorphism(data, invariant_clusters)
    end_isomorphism = time.time()

    # Total time
    total_time = (end_invariants - start_invariants) + (end_isomorphism - start_isomorphism)

    print(f"Time for clustering by invariants: {end_invariants - start_invariants:.2f} seconds")
    print(f"Time for post-clustering by isomorphism: {end_isomorphism - start_isomorphism:.2f} seconds")
    print(f"Total time: {total_time:.2f} seconds")

    # Output results
    print(f"Number of final clusters: {len(final_clusters)}")

    return final_clusters

# Run the main function
final_clusters = main()
