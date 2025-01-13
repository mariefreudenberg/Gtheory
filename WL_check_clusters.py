import pickle

# Lade Cluster-Ergebnisse
def load_clusters(filename):
    with open(filename, 'rb') as f:
        return pickle.load(f)

# Funktion zum Vergleichen der Cluster
def compare_clusters(clusters_a, clusters_b):
    # Sortiere die Gruppen und deren Mitglieder für einen robusten Vergleich
    sorted_a = [sorted(cluster) for cluster in clusters_a]
    sorted_b = [sorted(cluster) for cluster in clusters_b]

    # Sortiere die Cluster selbst
    sorted_a.sort()
    sorted_b.sort()

    # Vergleiche die Cluster
    return sorted_a == sorted_b

# Lade die gespeicherten Cluster
clusters_wl_hashing = load_clusters('clusters_wl_hashing.pkl')
clusters_recursive_wl = load_clusters('clusters_recursive_wl.pkl')

# Vergleich durchführen
are_identical = compare_clusters(clusters_wl_hashing, clusters_recursive_wl)

# Ergebnisse ausgeben
if are_identical:
    print("Die Cluster sind identisch: Alle Mitglieder wurden gleich gruppiert.")
else:
    print("Die Cluster unterscheiden sich: Es gibt Unterschiede in der Gruppenzuordnung.")

# Optionale Ausgabe der Unterschiede
def find_differences(clusters_a, clusters_b):
    sorted_a = [sorted(cluster) for cluster in clusters_a]
    sorted_b = [sorted(cluster) for cluster in clusters_b]
    sorted_a.sort()
    sorted_b.sort()

    # Unterschiede finden
    only_in_a = [cluster for cluster in sorted_a if cluster not in sorted_b]
    only_in_b = [cluster for cluster in sorted_b if cluster not in sorted_a]
    return only_in_a, only_in_b

if not are_identical:
    only_in_wl_hashing, only_in_recursive_wl = find_differences(clusters_wl_hashing, clusters_recursive_wl)
    print(f"Gruppen nur in WL-Hashing: {only_in_wl_hashing}")
    print(f"Gruppen nur in Recursive WL: {only_in_recursive_wl}")
