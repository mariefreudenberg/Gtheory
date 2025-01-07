import pickle

import networkx as nx

with open('rc_with_clusters.pkl', 'rb') as f:
    data = pickle.load(f)

G1 = data[0]['reaction_center']
G2 = data[1]['reaction_center']


def calculate_invariants(graph):
    vertex_count = graph.number_of_nodes()  # Anzahl der Knoten
    edge_count = graph.number_of_edges()    # Anzahl der Kanten
    degrees = sorted(dict(graph.degree()).values())  # Knotengrade (sortiert)
    density =  nx.density(graph)
    node_connectivity = nx.node_connectivity(graph)
    triangles = nx.triangles(graph)
    katz = nx.katz_centrality(graph)
    shortest_path =nx.average_shortest_path_length(graph)
    planarity = nx.check_planarity(graph)
    centrality = nx.degree_centrality(graph)

    return vertex_count, edge_count, degrees, density, node_connectivity, triangles, katz, shortest_path, planarity, centrality

# Invarianten für beide Graphen berechnen
invariants_G1 = calculate_invariants(G1)
invariants_G2 = calculate_invariants(G2)

# Vergleiche der Invarianten
print("Graph 1 Invarianten:", invariants_G1)
print("Graph 2 Invarianten:", invariants_G2)

if invariants_G1 == invariants_G2:
    print("Die Graph-Invarianten stimmen überein.")
else:
    print("Die Graph-Invarianten unterscheiden sich.")