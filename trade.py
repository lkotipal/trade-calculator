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
    nodes['Collecting Power'] = nodes['Total Power'] * nodes['Collecting Power']
    nodes['Transfer Power'] = nodes['Total Power'] * nodes['Transfer Power']
    nodes['Merchant Power'] = nodes['Transfer Power'] * nodes['Merchant Power']
    # Separate player power
    nodes['Total Power'] -= nodes['My Trade Power']
    nodes['Merchant Power'] -= nodes['My Trade Power'] * nodes['Steering']
    collecting = nodes['Collecting']
    transferring = ~collecting
    nodes.loc[collecting, 'Collecting Power'] -= nodes.loc[collecting, 'My Trade Power']
    nodes.loc[transferring, 'Transfer Power'] -= nodes.loc[transferring, 'My Trade Power']
    nodes['My Trade Power'] /= (1 + nodes['Power Modifier'])

    # Sort nodes
    nodes['Mark'] = 0
    sorted_nodes = []
    while (not nodes[nodes['Mark'] == 0].empty):
        sorted_nodes += visit(nodes, nodes[nodes['Mark'] == 0].iloc[0].name)
    nodes = nodes.loc[sorted_nodes[::-1]].drop('Mark', axis=1)
    return nodes

def calculate(nodes):
    nodes = nodes.copy()
    # Add player power
    nodes['My Trade Power'] *= (1 + nodes['Power Modifier'])
    nodes['Total Power'] += nodes['My Trade Power']
    collecting = nodes['Collecting']
    transferring = ~collecting
    nodes.loc[collecting, 'Collecting Power'] += nodes.loc[collecting, 'My Trade Power']
    nodes.loc[transferring, 'Transfer Power'] += nodes.loc[transferring, 'My Trade Power']
    nodes['Merchant Power'] += nodes['My Trade Power'] * nodes['Steering']
    
    # Calculate steering
    nodes['Merchant Power'] = nodes['Merchant Power'].apply(lambda x: x if np.sum(x) else np.ones_like(x))
    nodes['Total Power'] = nodes['Total Power'].apply(lambda x: x if x > 0 else 1)
    nodes['Steered'] = nodes['Transfer Power'] / nodes['Total Power'] * nodes['Merchant Power'] / (nodes['Merchant Power'].apply(lambda x: np.sum(x))) * (1.0 + nodes['Steering Bonus'])

    # Steer trade
    nodes['Total Value'] = nodes['Local Value']
    for name, data in nodes.iterrows():
        nodes.loc[data['To'], 'Total Value'] += data['Steered'] * data['Total Value']
        nodes.loc[name, 'Total Value'] *= data['Collecting Power'] / data['Total Power']

    # Calculate profits
    nodes['My Value'] = nodes['Collecting'] * (1 + nodes['Trade Efficiency']) * nodes['My Trade Power'] / nodes['Total Power'] * nodes['Total Value']
    return nodes

nodes = read_nodes()
value = calculate(nodes)['My Value'].sum()
print(f'{value:.3f}')
h = 0.001
for node in nodes[nodes['Total Power'] > 0].index:
    print(node)
    nodes.loc[node, 'My Trade Power'] += h
    print(f"1 power gives {(calculate(nodes)['My Value'].sum() - value) / h:.3f} dct")
    nodes.loc[node, 'My Trade Power'] -= h

    # Goods produced is given per annum
    nodes.loc[node, 'Local Value'] += h
    print(f"1 value gives {(calculate(nodes)['My Value'].sum() - value) / (12 * h):.3f} dct")
    nodes.loc[node, 'Local Value'] -= h
    print()
