import numpy as np
import pandas as pd
from sys import stderr

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

# Remove merchant and its effects from node
# Takes as input the DataFrame of nodes and the name of the node
def remove_merchant(nodes, node):
    nodes.loc[node, 'Merchant'] = False
    nodes.loc[node, 'Steering'][:] = False
    nodes.loc[node, 'Trade Efficiency'] -= 0.1
    nodes.loc[node, 'Power Modifier'] -= 0.05
    nodes.loc[node, 'Our Power'] -= 2

# Add a merchant to a node
# Takes as input the DataFrame of nodes, name of the node to add an to steer to
# If node == to, merchant is set to collect
def add_merchant(nodes, node, to):
    nodes.loc[node, 'Merchant'] = True
    if node != to:
        nodes.loc[node, 'Steering'][:] = [True if s == to else False for s in nodes.loc[node, 'To']]
    nodes.loc[node, 'Trade Efficiency'] += 0.1
    nodes.loc[node, 'Power Modifier'] += 0.05
    nodes.loc[node, 'Our Power'] += 2

# Attempt to optimize home node and merchant placement using a greedy algorithm
# Takes as input the DataFrame of nodes, 
def place_merchants(nodes):
    nodes = nodes.copy()
    # First remove and count all merchants
    merchants = 0
    for node in nodes[nodes['Merchant']].index:
        remove_merchant(nodes, node)
        merchants += 1
    nodes['Collecting'] = False

    # Iterate through all nodes to find best place to collect
    best_value = 0
    best_home = ""
    for node, data in nodes[nodes['Trade Power'] > 0].iterrows():
        nodes.loc[node, 'Collecting'] = True
        value = calculate_value(nodes)['My Value'].sum()
        print(f'{node}: {value:.3}', file=stderr)
        if value > best_value:
            best_home = node
            best_value = value
        nodes.loc[node, 'Collecting'] = False
    nodes.loc[best_home, 'Collecting'] = True
    print(f'Best home node: {best_home}')

    # Place merchants using a greedy algorithm
    best_value = calculate_value(nodes)['My Value'].sum()
    best_merchants = []
    for _ in range(merchants):
        best_fromto = ()
        for node, data in nodes[~nodes['Merchant'] & nodes['Trade Power'] > 0].iterrows():
            if data['Collecting']:
                # Only set merchants to collect in home node
                add_merchant(nodes, node, node)
                value = calculate_value(nodes)['My Value'].sum()
                if value > best_value:
                    best_fromto = (node, node)
                    best_value = value
                remove_merchant(nodes, node)
            else:
                # Otherwise try steering in every direction
                for to in data['To']:
                    add_merchant(nodes, node, to)
                    value = calculate_value(nodes)['My Value'].sum()
                    if value > best_value:
                        best_fromto = (node, to)
                        best_value = value
                    remove_merchant(nodes, node)
        # Add best merchant and continue
        add_merchant(nodes, best_fromto[0], best_fromto[1])
        best_merchants.append(best_fromto)
    
    # TODO: collecting outside home node

    print('Merchant placement:')
    for node, to in best_merchants:
        print(f'{node} -> {to}')
    
    return nodes
