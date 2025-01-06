import pickle
import networkx as nx

with open('rc_with_clusters.pkl', 'rb') as f:
    data = pickle.load(f)

print(data[0:50])