# -*- coding: utf-8 -*-
"""
Created on Fri Oct 31 11:11:38 2025

@author: Nel-Tech
"""

# -*- coding: utf-8 -*-
"""
Created on Fri Oct 31 11:01:46 2025

@author: Nel-Tech
"""

# -*- coding: utf-8 -*-
"""
Created on Fri Oct 31 10:53:29 2025

@author: Nel-Tech
"""

import csv
import random
import matplotlib.pyplot as plt
from collections import deque

# 1. Créer un graphe aléatoire de 250 sommets
n = 250
p = 0.03  # probabilité de connexion entre deux sommets

edges = []

# Générer les arêtes de façon aléatoire
for i in range(n):
    for j in range(i + 1, n):
        if random.random() < p:  # avec probabilité p, on crée une arête
            distance = random.randint(0, 7)
            edges.append((i, j, distance))

# Sauvegarde au format CSV
with open("contacts.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["id_client_1", "id_client_2", "distance_moyenne"])
    writer.writerows(edges)

print(f"Fichier contacts.csv généré avec succès ({len(edges)} connexions créées).")

# 2. Charger le graphe à partir du CSV (sans pandas)
edges_loaded = []
with open("contacts.csv", "r") as f:
    reader = csv.DictReader(f)
    for row in reader:
        u = int(row["id_client_1"])
        v = int(row["id_client_2"])
        distance = int(row["distance_moyenne"])
        edges_loaded.append((u, v, distance))

# 3. Construire une liste d’adjacence
graph = {i: [] for i in range(n)}
for u, v, d in edges_loaded:
    graph[u].append((v, d))
    graph[v].append((u, d))

# 4. Calculer le degré de chaque sommet
degrees = {node: len(neighbors) for node, neighbors in graph.items()}

# 5. Construire la distribution des degrés
plt.hist(list(degrees.values()), bins=range(max(degrees.values()) + 2))
plt.title("Distribution des degrés")
plt.xlabel("Degré")
plt.ylabel("Nombre de sommets")
plt.show()

# 6. Liste des 5 sommets à plus haut degré
top5_degree = sorted(degrees.items(), key=lambda x: x[1], reverse=True)[:5]
print("Top 5 sommets par degré :", top5_degree)


# 7. Calculer la proximité (closeness centrality)
from collections import deque

def bfs_distances(start, graph):
    """Retourne les distances minimales depuis start vers tous les autres sommets."""
    distances = {node: float('inf') for node in graph}
    distances[start] = 0
    queue = deque([start])  # file FIFO pour exploration en largeur

    while queue:
        current = queue.popleft()
        for neighbor, dist in graph[current]:
            new_dist = distances[current] + dist
            if new_dist < distances[neighbor]:
                distances[neighbor] = new_dist
                queue.append(neighbor)
    return distances


closeness = {}
for node in graph:
    distances = bfs_distances(node, graph)
    finite_distances = [d for d in distances.values() if d < float('inf') and d > 0]
    if finite_distances:
        closeness[node] = 1 / sum(finite_distances)
    else:
        closeness[node] = 0  # sommet isolé

# 8. Distribution de proximité
plt.hist(list(closeness.values()), bins=20)
plt.title("Distribution des proximités")
plt.xlabel("Proximité (closeness)")
plt.ylabel("Nombre de sommets")
plt.show()

# 9. 5 sommets à plus haute proximité
top5_proximite = sorted(closeness.items(), key=lambda x: x[1], reverse=True)[:5]
print("Top 5 sommets par proximité :", top5_proximite)

def propagation(graph, start, days):
    """
    Retourne le nombre de sommets atteints après 'days' jours
    (propagation simple sur le graphe non orienté)
    """
    visited = set([start])
    current = set([start])

    for _ in range(days):
        next_nodes = set()
        for node in current:
            # on ajoute les voisins du noeud courant
            neighbors = [v for v, _ in graph[node]]  # extraire uniquement les sommets voisins
            next_nodes.update(neighbors)
        next_nodes -= visited
        if not next_nodes:
            break
        visited.update(next_nodes)
        current = next_nodes
    return len(visited)


# Campagne démarrée au sommet de plus haut degré
sommet_max_deg = top5_degree[0][0]
touches_5j = propagation(graph, sommet_max_deg, 5)
print("Sommets touchés après 5 jours (haut degré):", touches_5j)

# Campagne démarrée au sommet de plus haute proximité
sommet_max_prox = top5_proximite[0][0]
touches_7j = propagation(graph, sommet_max_prox, 7)
print("Sommets touchés après 7 jours (haute proximité):", touches_7j)

# La suite du projet

# 10. Suppression des sommets les plus centraux (haut degré et haute proximité)
to_remove = {node for node, _ in top5_degree + top5_proximite}

# Copier le graphe original
graph_removed = {node: [(v, d) for v, d in neighbors if v not in to_remove]
                 for node, neighbors in graph.items() if node not in to_remove}

print(f"Sommets supprimés : {sorted(to_remove)}")
print(f"Nouveau graphe : {len(graph_removed)} sommets restants")

# Sauvegarde du nouveau graphe
with open("contacts_modifie.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["id_client_1", "id_client_2", "distance_moyenne"])
    for u, neighbors in graph_removed.items():
        for v, d in neighbors:
            # pour éviter les doublons (écrire chaque arête une seule fois)
            if u < v:
                writer.writerow([u, v, d])

print("Fichier contacts_modifie.csv généré avec succès.")

# 11. Recalcul du degré et de la proximité dans le nouveau graphe

degrees2 = {node: len(neighbors) for node, neighbors in graph_removed.items()}

def bfs_distances(start, graph):
    """Distances minimales (comme avant)."""
    distances = {node: float('inf') for node in graph}
    distances[start] = 0
    queue = deque([start])
    while queue:
        current = queue.popleft()
        for neighbor, dist in graph[current]:
            new_dist = distances[current] + dist
            if new_dist < distances[neighbor]:
                distances[neighbor] = new_dist
                queue.append(neighbor)
    return distances

closeness2 = {}
for node in graph_removed:
    distances = bfs_distances(node, graph_removed)
    finite_distances = [d for d in distances.values() if d < float('inf') and d > 0]
    if finite_distances:
        closeness2[node] = 1 / sum(finite_distances)
    else:
        closeness2[node] = 0

# 12. Sélection des sommets extrêmes
sommet_max_deg2 = max(degrees2, key=degrees2.get)
sommet_min_prox2 = min(closeness2, key=closeness2.get)

# 13. Nouvelles propagations
touches_4j = propagation(graph_removed, sommet_max_deg2, 4)
touches_3j = propagation(graph_removed, sommet_min_prox2, 3)

print("Sommets touchés après 4 jours (haut degré, nouveau graphe):", touches_4j)
print("Sommets touchés après 3 jours (basse proximité, nouveau graphe):", touches_3j)

