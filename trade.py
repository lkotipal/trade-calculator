import numpy as np
import pandas as pd
from sys import setrecursionlimit

def visit(nodes, node):
    sorted_nodes = pd.DataFrame()
    if nodes.loc[node, 'Mark'] == 2:
        return sorted_nodes
    elif nodes.loc[node, 'Mark'] == 1:
        raise RuntimeError(f'Node {node} visited twice!')
    
    nodes.loc[node, 'Mark'] = 1
    for m in nodes.loc[node, 'To']:
        sorted_nodes = sorted_nodes.append(visit(nodes, m))
    
    nodes.loc[node, 'Mark'] = 2
    return sorted_nodes.append(nodes.loc[node])

setrecursionlimit(1000)
nodes = pd.read_csv('nodes.csv', index_col=0)
edges = pd.read_csv('edges.csv').groupby('From').agg(lambda x: list(x))
nodes = nodes.merge(edges, left_index=True, right_index=True, how='left')
isna = nodes['To'].isna()
nodes.loc[isna, 'To'] = pd.Series([[]] * isna.sum()).values
nodes.loc[isna, 'Steering Bonus'] = pd.Series([[]] * isna.sum()).values
nodes.loc[isna, 'Merchant Power'] = pd.Series([[]] * isna.sum()).values

nodes['Merchant Power'] = nodes['Merchant Power'].apply(np.array).apply(lambda x: x if np.sum(x) else np.ones_like(x))

nodes['Steering Bonus'] = nodes['Steering Bonus'].apply(np.array)

nodes['Retained'] = nodes['Collecting Power'] / (nodes['Transfer Power'] + nodes['Collecting Power'])
nodes['Steered'] = (1.0 - nodes['Retained']) * nodes['Merchant Power'] / (nodes['Merchant Power'].apply(lambda x: np.sum(x))) * (1.0 + nodes['Steering Bonus'])
nodes['Total Value'] = nodes['Local Value']

nodes['Mark'] = 0
sorted_nodes = pd.DataFrame()
while (not nodes[nodes['Mark'] == 0].empty):
    sorted_nodes = sorted_nodes.append(visit(nodes, nodes[nodes['Mark'] == 0].iloc[0].name))
nodes = sorted_nodes[::-1].drop('Mark', axis=1)   # Convention

for name, data in nodes.iterrows():
    nodes.loc[data['To'], 'Total Value'] += data['Steered'] * data['Total Value']
    nodes.loc[name, 'Total Value'] *= data['Retained']

nodes['My Value'] = nodes['Collecting'] * (1 + nodes['My Trade Efficiency']) * nodes['My Trade Power'] / (nodes['Transfer Power'] + nodes['Collecting Power']) * nodes['Total Value']
print(nodes)
