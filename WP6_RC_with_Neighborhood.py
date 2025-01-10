import pickle
import networkx as nx
from networkx import ego_graph
import matplotlib.pyplot as plt
from synutility.SynVis.graph_visualizer import GraphVisualizer


# Function to compute the reaction center and its k-hop neighborhood
def compute_reaction_center_with_neighborhood(graph, k_hop=1):
    # Extract the reaction center (edges with 'standard_order' != 0)
    rc_subgraph = nx.edge_subgraph(graph, [(e[0], e[1]) for e in graph.edges(data=True) if e[2]['standard_order'] != 0])
    rc_nodes = list(rc_subgraph.nodes)

    # Expand to the k-hop neighborhood
    neighborhood_subgraph = nx.Graph()
    for node in rc_nodes:
        # Add k-hop neighborhood around each node in the reaction center
        ego = ego_graph(graph, node, radius=k_hop)
        neighborhood_subgraph = nx.compose(neighborhood_subgraph, ego)

    return neighborhood_subgraph


# Main processing
if __name__ == "__main__":
    # Load data
    with open('ITS_graphs.pkl', 'rb') as f:
        data = pickle.load(f)

    # Define k-hop parameter
    k_hop = 2

    # Compute reaction centers with neighborhoods for the entire dataset
    reaction_centers_with_neighborhoods = []
    for item in data:
        graph = item['ITS']
        rc_with_neighborhood = compute_reaction_center_with_neighborhood(graph, k_hop=k_hop)
        reaction_centers_with_neighborhoods.append(
            {'R-id': item['R-id'], 'reaction_center': rc_with_neighborhood}) # R-id for small, R_ID for large dataset

    # Save the reaction centers with neighborhoods to a new pickle file
    output_file = f'Small_RCs_khop_{k_hop}.pkl'
    with open(output_file, 'wb') as f:
        pickle.dump(reaction_centers_with_neighborhoods, f)

    print(f"Reaction centers with {k_hop}-hop neighborhoods saved to {output_file}")

    # Visualization example for the first graph
    fig, ax = plt.subplots(2, 1, figsize=(15, 10))
    vis = GraphVisualizer()
    vis.plot_its(data[1]['ITS'], ax[0], use_edge_color=True)
    vis.plot_its(reaction_centers_with_neighborhoods[1]['reaction_center'], ax[1],
                 use_edge_color=True)
    plt.show()
