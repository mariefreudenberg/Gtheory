import matplotlib.pyplot as plt
import numpy as np


def plot_grouped_bar_chart(data, categories, khop_labels, title="Laufzeiten für Clustering", ylabel="Laufzeit (s)"):
    """
    Erstellt ein gruppiertes Balkendiagramm für die Clustering-Laufzeiten.

    Parameters:
    - data: 2D-Liste mit den Laufzeiten, geordnet nach [Kategorie][khop]
    - categories: Liste der Kategorien (z. B. ["is_isomorphic", "Invariants", "WL"])
    - khop_labels: Liste der khop-Werte (z. B. ["khop1", "khop2", "khop3"])
    - title: Titel des Diagramms
    - ylabel: Beschriftung der y-Achse
    """
    n_categories = len(categories)
    n_khops = len(khop_labels)

    # Positionen der Gruppen auf der x-Achse
    x = np.arange(n_khops)
    width = 0.8 / n_categories  # Breite der Balken pro Kategorie

    # Erstelle die Balken
    fig, ax = plt.subplots(figsize=(10, 6))
    for i, category in enumerate(categories):
        ax.bar(x + i * width, data[i], width, label=category)

    # Diagramm anpassen
    ax.set_title(title)
    ax.set_xlabel("khop")
    ax.set_ylabel(ylabel)
    ax.set_xticks(x + (n_categories - 1) * width / 2)
    ax.set_xticklabels(khop_labels)
    ax.legend()
    ax.grid(axis="y", linestyle="--", alpha=0.7)

    # Diagramm anzeigen
    plt.tight_layout()
    plt.show()


# Beispiel-Daten (kannst du durch deine Daten ersetzen)
categories = ["is_isomorphic", "Invariants (element_bond)", "WL (1 iteration)"]
khop_labels = ["khop1", "khop2", "khop3"]
data = [
    [22.75, 79.5, 839.02],  # Laufzeiten für is_isomorphic
    [2.46, 3.86, 6.24],  # Laufzeiten für Invariants (element_bond)
    [2.19, 3.98, 5.89]  # Laufzeiten für WL (1 iteration)
]

# Diagramm erstellen
plot_grouped_bar_chart(data, categories, khop_labels)
