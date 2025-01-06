import pickle
import networkx as nx

with open('reaction_centers.pkl', 'rb') as f:
    data = pickle.load(f)

#print(data)

rc0 = data[0]['reaction_center']
rc1 = data[1]['reaction_center']
rc2 = data[2]['reaction_center']
rc3 = data[3]['reaction_center']
rc4 = data[4]['reaction_center']

#node match function
def node_match(n1, n2):
    return n1['charge'] == n2['charge'] and n1['element'] == n2['element']

def edge_match(e1, e2):
    return e1['order'] == e2['order']

#are_isomorphic = nx.is_isomorphic(rc0, rc4, node_match=node_match, edge_match=edge_match)
#print("Are the graphs isomorphic with atom labels considered?", are_isomorphic)


# Function to cluster reaction centers based on isomorphism
def cluster_reaction_centers(data):
    clusters = []  # List of groups, each group is a list of indices or RCs

    for i, rc in enumerate(data):
        is_added = False
        for group in clusters:
            # Compare the RC to the first RC in the group
            representative_rc = data[group[0]]['reaction_center']
            if nx.is_isomorphic(rc['reaction_center'], representative_rc, node_match=node_match, edge_match=edge_match):
                group.append(i)
                is_added = True
                break

        # If no group matches, create a new group
        if not is_added:
            clusters.append([i])

    return clusters

cluster = cluster_reaction_centers(data)
# Print results
for i, group in enumerate(cluster):
    print(f"Group {i + 1}: {group}")

# Add group number to the data
def add_group_numbers(data, clusters):
    # Create a mapping of index to group number
    index_to_group = {}
    for group_num, group in enumerate(clusters, start=1):
        for idx in group:
            index_to_group[idx] = group_num

    # Add the group number to each RC in data
    for i, rc in enumerate(data):
        rc['group'] = index_to_group[i]

    return data

# Main workflow
def process_and_save(data, output_file):
    # Step 1: Cluster reaction centers
    clusters = cluster_reaction_centers(data)

    # Step 2: Add group numbers to the data
    data_with_groups = add_group_numbers(data, clusters)

    # Step 3: Save the updated data to a pickle file
    with open(output_file, 'wb') as f:
        pickle.dump(data_with_groups, f)

    print(f"Updated data saved to {output_file}")
    return data_with_groups

output_file = 'rc_with_clusters.pkl'
data_with_groups = process_and_save(data, output_file)

