import pickle
import networkx as nx

# Laden der Daten
with open('reaction_centers.pkl', 'rb') as f:
    data = pickle.load(f)


# Funktion zur Berechnung der Invarianten
def calculate_invariants(graph):
    #vertex_count = graph.number_of_nodes()  # Anzahl der Knoten
    #edge_count = graph.number_of_edges()  # Anzahl der Kanten
    degrees = sorted(dict(graph.degree()).values())  # Knotengrade (sortiert)
    density = nx.density(graph)
    #planarity = nx.is_planar(graph) #only one group: all planar
    #node_connectivity = nx.node_connectivity(graph)
    #triangles = sum(nx.triangles(graph).values())  # Gesamtanzahl der Dreiecke
    #centrality = nx.degree_centrality(graph)  # Dictionary mit Zentralitäten: 19427 groups is way too much
    avg_shortest_path = (
        nx.average_shortest_path_length(graph)
        if nx.is_connected(graph) else None
    )  # Nur berechnen, wenn der Graph zusammenhängend ist
    return (
        #vertex_count,
        #edge_count,
        degrees,
        density,
        #planarity,
        #node_connectivity,
        #triangles,
        #centrality,
        avg_shortest_path,
    )


# Funktion zur Gruppierung nach Invarianten
def cluster_by_invariants(data):
    clusters = []  # Liste der Gruppen
    invariants_per_group = []  # Liste der Invarianten für jede Gruppe

    for i, rc in enumerate(data):
        invariants = calculate_invariants(rc['reaction_center'])  # Invarianten berechnen
        is_added = False

        # Vergleiche mit jeder bestehenden Gruppe
        for group_idx, group_invariants in enumerate(invariants_per_group):
            if invariants == group_invariants:  # Gleiche Invarianten
                clusters[group_idx].append(i)  # Füge zur Gruppe hinzu
                is_added = True
                break

        # Falls keine passende Gruppe gefunden, neue Gruppe erstellen
        if not is_added:
            clusters.append([i])
            invariants_per_group.append(invariants)

    return clusters, invariants_per_group


def analyze_invariants_divisions(data):
    unique_values_per_invariant = {}

    # Calculate all invariants for each RC
    all_invariants = [calculate_invariants(rc['reaction_center']) for rc in data]

    # For each invariant position (e.g., Vertex Count, Edge Count)
    for i in range(len(all_invariants[0])):
        # Convert mutable objects (like dicts) to hashable objects
        unique_values = set(
            tuple(invariant[i].items()) if isinstance(invariant[i], dict) else
            tuple(invariant[i]) if isinstance(invariant[i], list) else
            invariant[i]
            for invariant in all_invariants
        )
        unique_values_per_invariant[i] = len(unique_values)

    return unique_values_per_invariant


# Group RCs by invariants
clusters, invariants_per_group = cluster_by_invariants(data)

# Analyze divisions created by each invariant
invariant_divisions = analyze_invariants_divisions(data)


# Ergebnisse ausgeben
print(f"Anzahl der Gruppen basierend auf Invarianten: {len(clusters)}")
for i, group in enumerate(clusters):
    print(f"Gruppe {i + 1}: {group}")

print("\nAnzahl der Unterteilungen durch jede Invariante:")
for invariant_idx, division_count in invariant_divisions.items():
    print(f"Invariante {invariant_idx + 1}: {division_count} Unterteilungen")
