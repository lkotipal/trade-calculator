import numpy as np
import pandas as pd

# Topological sort algorithm
def visit(nodes, node):
    sorted_nodes = []
    if nodes.loc[node, 'Mark'] == 2:
        return sorted_nodes
    elif nodes.loc[node, 'Mark'] == 1:
        raise RuntimeError(f'Node {node} visited twice!')
    
    nodes.loc[node, 'Mark'] = 1
    for m in nodes.loc[node, 'To']:
        sorted_nodes += visit(nodes, m)
    
    nodes.loc[node, 'Mark'] = 2
    sorted_nodes.append(node)
    return sorted_nodes

def read_nodes():
    # Read data
    nodes = pd.read_csv('nodes.csv', index_col=0)
    edges = pd.read_csv('edges.csv').groupby('From').agg(lambda x: list(x))
    nodes = nodes.merge(edges, left_index=True, right_index=True, how='left')
    # Null data to empty lists
    isna = nodes['To'].isna()
    nodes.loc[isna, 'To'] = pd.Series([[]] * isna.sum()).values
    nodes.loc[isna, 'Steering Bonus'] = pd.Series([[]] * isna.sum()).values
    nodes.loc[isna, 'Merchant Power'] = pd.Series([[]] * isna.sum()).values
    # Lists to Numpy arrays
    nodes['Merchant Power'] = nodes['Merchant Power'].apply(np.array)
    nodes['Steering Bonus'] = nodes['Steering Bonus'].apply(np.array)
    nodes['Steering'] = nodes['Steering'].apply(np.array)
    # Percentage -> number
    nodes['Collecting Power'] = nodes['Trade Power'] * nodes['Collecting Power']
    nodes['Transfer Power'] = nodes['Trade Power'] * nodes['Transfer Power']
    nodes['Merchant Power'] = nodes['Transfer Power'] * nodes['Merchant Power'] # TODO THIS IS WRONG :D
    # Separate player power
    nodes['Trade Power'] -= nodes['Our Power']
    nodes['Merchant Power'] -= nodes['Our Power'] * nodes['Steering']
    collecting = nodes['Collecting']
    transferring = ~collecting
    nodes.loc[collecting, 'Collecting Power'] -= nodes.loc[collecting, 'Our Power']
    nodes.loc[transferring, 'Transfer Power'] -= nodes.loc[transferring, 'Our Power']
    nodes['Our Power'] /= (1 + nodes['Power Modifier'])
    nodes.loc[nodes['Collecting'], 'Power Modifier'] -= 0.1 * nodes['Steering'].apply(np.sum).sum()
    nodes['Privateer Power'] = 0

    # Sort nodes
    nodes['Mark'] = 0
    sorted_nodes = []
    while (not nodes[nodes['Mark'] == 0].empty):
        sorted_nodes += visit(nodes, nodes[nodes['Mark'] == 0].iloc[0].name)
    nodes = nodes.loc[sorted_nodes[::-1]].drop('Mark', axis=1)
    return nodes

def calculate_value(nodes):
    nodes = nodes.copy()
    # Add player power
    nodes.loc[nodes['Collecting'], 'Power Modifier'] += 0.1 * nodes['Steering'].apply(np.sum).sum()
    nodes['Our Power'] *= (1 + nodes['Power Modifier'])
    nodes['Privateer Efficiency'] = nodes['Privateer Efficiency'].fillna(-1)
    nodes['Privateer Power'] *= 1.5 * (1 + nodes['Privateer Efficiency'])
    nodes['Trade Power'] += nodes['Our Power'] + nodes['Privateer Power']
    collecting = nodes['Collecting']
    transferring = ~collecting
    nodes.loc[collecting, 'Collecting Power'] += nodes.loc[collecting, 'Our Power']
    nodes.loc[transferring, 'Transfer Power'] += nodes.loc[transferring, 'Our Power']
    nodes['Merchant Power'] += nodes['Our Power'] * nodes['Steering']
    
    # Calculate steering
    nodes['Merchant Power'] = nodes['Merchant Power'].apply(lambda x: x if np.sum(x) else np.ones_like(x))
    nodes['Steered'] = nodes['Transfer Power'] / nodes['Trade Power'] * nodes['Merchant Power'] / (nodes['Merchant Power'].apply(lambda x: np.sum(x))) * (1.0 + nodes['Steering Bonus'])

    # Steer trade
    nodes['Total Value'] = nodes['Local Value']
    for node in nodes[nodes['Trade Power'] > 0].index:
        nodes.loc[nodes.loc[node, 'To'], 'Total Value'] += nodes.loc[node, 'Steered'] * nodes.loc[node, 'Total Value']
        nodes.loc[node, 'Total Value'] *= nodes.loc[node, 'Collecting Power'] / nodes.loc[node, 'Trade Power']

    # Calculate profits
    nodes['My Value'] = (nodes['Collecting'] * (1 + nodes['Trade Efficiency']) * nodes['Our Power'] / nodes['Collecting Power'] + nodes['Privateer Power'] / (2 * nodes['Trade Power'])) * nodes['Total Value']
    return nodes
