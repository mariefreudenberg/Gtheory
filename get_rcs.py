import pickle
import networkx as nx

from Documents.files.src.rc_extract import get_rc

with open('ITS_largerdataset.pkl', 'rb') as f:
    data = pickle.load(f)

# Extracting reaction center and plotting using SynUtils
G = data[1]['ITS']
reaction_center = nx.edge_subgraph(G,\
                                   [(e[0],e[1]) for e in G.edges(data=True) \
                                    if e[2]['standard_order']!=0])

from synutility.SynVis.graph_visualizer import GraphVisualizer
import matplotlib.pyplot as plt

#Extract RC from all graphs and save them in an extra file

def compute_reaction_center(graph):
    # Filter edges with 'standard_order' != 0 and create the subgraph
    subgraph = nx.edge_subgraph(graph, [(e[0], e[1]) for e in graph.edges(data=True) if e[2]['standard_order'] != 0])
    return nx.Graph(subgraph)  # Convert to a standalone Graph

# Compute reaction centers for the entire dataset
reaction_centers = []
for item in data:
    graph = item['ITS']
    rc = compute_reaction_center(graph)
    reaction_centers.append({'R_ID': item['R_ID'], 'reaction_center': rc}) #R-id for small, R_ID for large dataset

# Save the reaction centers to a file
with open('Larger_rcs.pkl', 'wb') as f:
    pickle.dump(reaction_centers, f)

print("Reaction centers saved to reaction_centers.pkl")


fig, ax = plt.subplots(2, 1, figsize=(15, 10))
vis = GraphVisualizer()
vis.plot_its(data[1]['ITS'], ax[0], use_edge_color=True)
vis.plot_its(reaction_center, ax[1], use_edge_color=True)
plt.show()

"""
graph1 = data[0]['ITS']
graph2 = data[1]['ITS']

are_isomorphic = nx.is_isomorphic(graph1, graph2)

# Print the result
print("Are the graphs isomorphic?", are_isomorphic)
"""
