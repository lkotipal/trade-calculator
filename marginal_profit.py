import numpy as np
import pandas as pd
from nodes import calculate_value, read_nodes
from sys import stderr

def main():
    nodes = read_nodes()
    nodes2 = calculate_value(nodes)
    print(nodes2.loc[nodes['Local Value'] > 0, 'Total Value'].to_string(), file=stderr)
    value = nodes2['My Value'].sum()
    print(f'Current profit: {value:.3f} dct')

    h = 0.001
    print('Marginal profit:')
    nodes['Power Modifier'] += h
    print(f"1% global trade power gives {(calculate_value(nodes)['My Value'].sum() - value) / (100 * h):.3f} dct")
    nodes['Power Modifier'] -= h

    nodes['Trade Efficiency'] += h
    print(f"1% trade efficiency gives {(calculate_value(nodes)['My Value'].sum() - value) / (100 * h):.3f} dct")
    nodes['Trade Efficiency'] -= h

    marginal_profits = pd.DataFrame(columns=('dct / power', 'dct / value'))
    for node in nodes[nodes['Trade Power'] > 0].index:
        nodes.loc[node, 'Our Power'] += h
        power_profit = (calculate_value(nodes)['My Value'].sum() - value) / h
        nodes.loc[node, 'Our Power'] -= h

        # Goods produced is given per annum
        nodes.loc[node, 'Local Value'] += h
        value_profit = (calculate_value(nodes)['My Value'].sum() - value) / (12 * h)
        nodes.loc[node, 'Local Value'] -= h

        marginal_profits.loc[node] = [power_profit, value_profit]
    
    print(marginal_profits, file=stderr)

    idx = marginal_profits['dct / power'].idxmax()
    print(f"Best profit from trade power {marginal_profits.loc[idx, 'dct / power']:.3} dct at {idx}")
    idx = marginal_profits['dct / value'].idxmax()
    print(f"Best profit from trade value {marginal_profits.loc[idx, 'dct / value']:.3f} dct at {idx}")

if __name__ == '__main__':
    main()