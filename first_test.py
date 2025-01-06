import pickle
import networkx as nx

from Documents.files.src.rc_extract import get_rc

with open('/u/home/gpraktikum/Documents/files/ITS_graphs.pkl', 'rb') as f:
    data = pickle.load(f)

# Using SynUtils
from synutility.SynIO.data_type import load_from_pickle
data = load_from_pickle('/u/home/gpraktikum/Documents/files/ITS_graphs.pkl')

# Extracting reaction center and plotting using SynUtils
from src.rc_extract import get_rc
reaction_center = get_rc(data[1]['ITS'])

from synutility.SynVis.graph_visualizer import GraphVisualizer
import matplotlib.pyplot as plt

#Extract RC from all graphs and save them in an extra file
import pickle
from src.rc_extract import get_rc

# List to store reaction centers
reaction_centers = []

# Extract RC for each graph in the dataset
for item in data:
    graph = item['ITS']
    rc = get_rc(graph)
    reaction_centers.append({'R-id': item['R-id'], 'reaction_center': rc})

# Save the reaction centers to a file
with open('reaction_centers.pkl', 'wb') as f:
    pickle.dump(reaction_centers, f)

print("Reaction centers saved to reaction_centers.pkl")

fig, ax = plt.subplots(2, 1, figsize=(15, 10))
vis = GraphVisualizer()
vis.plot_its(data[1]['ITS'], ax[0], use_edge_color=True)
vis.plot_its(reaction_center, ax[1], use_edge_color=True)
plt.show()


graph1 = data[0]['ITS']
graph2 = data[1]['ITS']

are_isomorphic = nx.is_isomorphic(graph1, graph2)

# Print the result
print("Are the graphs isomorphic?", are_isomorphic)
