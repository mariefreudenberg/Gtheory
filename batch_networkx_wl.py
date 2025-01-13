import pickle
import networkx as nx
from networkx.algorithms.graph_hashing import weisfeiler_lehman_graph_hash
import time
import csv
from synutility.SynVis.graph_visualizer import GraphVisualizer

# Function to split the dataset into batches
def split_dataset(data, num_batches):
    batch_size = len(data) // num_batches
    return [data[i * batch_size: (i + 1) * batch_size] for i in range(num_batches)]

# Function to prepare aggregated node attributes
def prepare_node_attributes(graph):
    for node, attrs in graph.nodes(data=True):
        attrs['aggregated'] = f"{attrs['element']}_{attrs['charge']}"

# Function to calculate WL graph hash
def calculate_wl_hash(graph):
    prepare_node_attributes(graph)
    return weisfeiler_lehman_graph_hash(graph, node_attr='aggregated', edge_attr='order', iterations=3)

# Function to cluster by WL graph hash
def cluster_by_wl_hash(data_batch):
    clusters = {}
    for i, rc in enumerate(data_batch):
        wl_hash = calculate_wl_hash(rc['reaction_center'])
        if wl_hash not in clusters:
            clusters[wl_hash] = []
        clusters[wl_hash].append(i)
    return list(clusters.values())

# Function to post-cluster by isomorphism
def postcluster_by_isomorphism(data_batch, invariant_clusters):
    final_clusters = []
    for group in invariant_clusters:
        sub_clusters = []
        for idx in group:
            rc = data_batch[idx]['reaction_center']
            is_added = False
            for sub_cluster in sub_clusters:
                representative_rc = data_batch[sub_cluster[0]]['reaction_center']
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
def process_batch(data_batch, batch_idx):
    # Step 1: WL Clustering
    start_wl = time.time()
    wl_clusters = cluster_by_wl_hash(data_batch)
    end_wl = time.time()
    wl_time = end_wl - start_wl

    # Step 2: Post-clustering by isomorphism
    start_iso = time.time()
    final_clusters = postcluster_by_isomorphism(data_batch, wl_clusters)
    end_iso = time.time()
    iso_time = end_iso - start_iso

    total_time = wl_time + iso_time
    print(f"Batch {batch_idx}: WL Clusters = {len(wl_clusters)}, Isomorphic Clusters = {len(final_clusters)}")
    print(f"Batch {batch_idx}: WL Time = {wl_time:.2f}s, Isomorphism Time = {iso_time:.2f}s, Total Time = {total_time:.2f}s")

    return {
        "Batch": batch_idx,
        "WL Clusters": len(wl_clusters),
        "Isomorphic Clusters": len(final_clusters),
        "WL Time (s)": wl_time,
        "Isomorphism Time (s)": iso_time,
        "Total Time (s)": total_time
    }

# Main function
def main():
    # Load data
    with open('Larger_rcs.pkl', 'rb') as f:
        data = pickle.load(f)

    # Split data into batches
    num_batches = 20
    batches = split_dataset(data, num_batches)

    # Process each batch
    results = []
    for batch_idx, batch in enumerate(batches, start=1):
        result = process_batch(batch, batch_idx)
        results.append(result)

    # Save results to CSV
    output_file = 'Large_batch_networkx_wl_results.csv'
    with open(output_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["Batch", "WL Clusters", "Isomorphic Clusters", "WL Time (s)", "Isomorphism Time (s)", "Total Time (s)"])
        writer.writeheader()
        writer.writerows(results)

    print(f"Results saved to {output_file}")

if __name__ == "__main__":
    main()
