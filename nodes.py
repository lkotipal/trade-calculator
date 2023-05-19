import numpy as np
import pandas as pd

# Topological sort algorithm
# Takes as input the DataFrame of nodes and the name of the node to start from
def visit(nodes, node):
    sorted_nodes = []
    # Node is finished already
    if nodes.loc[node, 'Mark'] == 2:
        return sorted_nodes
    # Node was visited already, this should not happen in a DAG
    elif nodes.loc[node, 'Mark'] == 1:
        raise RuntimeError(f'Node {node} visited twice!')
    
    # Recursively sort nodes downstream
    nodes.loc[node, 'Mark'] = 1
    for m in nodes.loc[node, 'To']:
        sorted_nodes += visit(nodes, m)
    
    nodes.loc[node, 'Mark'] = 2
    sorted_nodes.append(node)
    return sorted_nodes

# Read nodes from files nodes.csv and edges.csv
def read_nodes():
    # Read data
    nodes = pd.read_csv('nodes.csv', index_col=0)
    edges = pd.read_csv('edges.csv').groupby('From').agg(lambda x: list(x))
    nodes = nodes.merge(edges, left_index=True, right_index=True, how='left')
    # Null data to empty lists
    isna = nodes['To'].isna()
    nodes.loc[isna, 'To'] = pd.Series([[]] * isna.sum()).values
    nodes.loc[isna, 'Merchant Bonus'] = pd.Series([[]] * isna.sum()).values
    nodes.loc[isna, 'Merchant Power'] = pd.Series([[]] * isna.sum()).values
    # Lists to Numpy arrays
    nodes['Merchant Power'] = nodes['Merchant Power'].apply(np.array)
    nodes['Merchant Bonus'] = nodes['Merchant Bonus'].apply(np.array)
    nodes['Steering'] = nodes['Steering'].apply(np.array)
    nodes['Steering Bonus'] = nodes['Steering Bonus'].apply(np.array)
    # Percentage -> number
    nodes['Collecting Power'] = nodes['Trade Power'] * nodes['Collecting Power']
    nodes['Transfer Power'] = nodes['Trade Power'] * nodes['Transfer Power']
    # Separate player power
    nodes['Trade Power'] -= nodes['Our Power']
    nodes['Merchant Power'] -= nodes['Our Power'] * nodes['Steering'] * (1 + nodes['Steering Bonus'])
    collecting = nodes['Collecting']
    transferring = ~collecting
    nodes.loc[collecting, 'Collecting Power'] -= nodes.loc[collecting, 'Our Power']
    nodes.loc[transferring, 'Transfer Power'] -= nodes.loc[transferring, 'Our Power']
    nodes['Our Power'] /= (1 + nodes['Power Modifier'])
    nodes.loc[nodes['Collecting'], 'Power Modifier'] -= 0.1 * nodes['Steering'].apply(np.sum).sum()

    # Sort nodes
    nodes['Mark'] = 0
    sorted_nodes = []
    while (not nodes[nodes['Mark'] == 0].empty):
        # Add to list results of topological sort from the first node not sorted
        sorted_nodes += visit(nodes, nodes[nodes['Mark'] == 0].iloc[0].name)
    nodes = nodes.loc[sorted_nodes[::-1]].drop('Mark', axis=1)
    return nodes

# Perform calculations to get the final value on a copy of nodes
# Takes as input the original nodes, returns a copy with all values calculated for nodes with non-zero trade power
def calculate_value(nodes):
    nodes = nodes.copy()
    # Add player power
    nodes.loc[nodes['Collecting'], 'Power Modifier'] += 0.1 * nodes['Steering'].apply(np.sum).sum()
    nodes['Our Power'] *= (1 + nodes['Power Modifier'])
    nodes['Trade Power'] += nodes['Our Power']
    collecting = nodes['Collecting']
    transferring = ~collecting
    nodes.loc[collecting, 'Collecting Power'] += nodes.loc[collecting, 'Our Power']
    nodes.loc[transferring, 'Transfer Power'] += nodes.loc[transferring, 'Our Power']
    nodes['Merchant Power'] += nodes['Our Power'] * nodes['Steering'] * (1 + nodes['Steering Bonus'])
    
    # Calculate value steered
    nodes['Merchant Power'] = nodes['Merchant Power'].apply(lambda x: x if np.sum(x) else np.ones_like(x))
    nodes['Steered'] = nodes['Transfer Power'] / nodes['Trade Power'] * nodes['Merchant Power'] / (nodes['Merchant Power'].apply(lambda x: np.sum(x))) * (1.0 + nodes['Merchant Bonus'])

    # Steer trade one node at a time
    nodes['Total Value'] = nodes['Local Value']
    for node in nodes[nodes['Trade Power'] > 0].index:
        nodes.loc[nodes.loc[node, 'To'], 'Total Value'] += nodes.loc[node, 'Steered'] * nodes.loc[node, 'Total Value']
        nodes.loc[node, 'Total Value'] *= nodes.loc[node, 'Collecting Power'] / nodes.loc[node, 'Trade Power']

    # Calculate final profits
    nodes['My Value'] = (nodes['Collecting'] * (1 + nodes['Trade Efficiency']) * nodes['Our Power'] / nodes['Collecting Power']) * nodes['Total Value']
    return nodes
