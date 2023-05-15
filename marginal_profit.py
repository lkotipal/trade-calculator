import numpy as np
import pandas as pd
from nodes import calculate_value, read_nodes

def main():
    nodes = read_nodes()
    value = calculate_value(nodes)['My Value'].sum()
    print(f'Profit: {value:.3f} dct')
    print()

    h = 0.001
    print('Marginal profit:')
    nodes['Power Modifier'] += h
    print(f"1% global trade power gives {(calculate_value(nodes)['My Value'].sum() - value) / (100 * h):.3f} dct")
    nodes['Power Modifier'] -= h
    print()

    nodes['Trade Efficiency'] += h
    print(f"1% trade efficiency gives {(calculate_value(nodes)['My Value'].sum() - value) / (100 * h):.3f} dct")
    nodes['Trade Efficiency'] -= h
    print()

    marginal_profits = pd.DataFrame(columns=('dct / power', 'dct / privateer', 'dct / value'))
    for node in nodes[nodes['Trade Power'] > 0].index:
        nodes.loc[node, 'Our Power'] += h
        power_profit = (calculate_value(nodes)['My Value'].sum() - value) / h
        nodes.loc[node, 'Our Power'] -= h

        nodes.loc[node, 'Privateer Power'] += h
        privateer_profit = (calculate_value(nodes)['My Value'].sum() - value) / h
        nodes.loc[node, 'Privateer Power'] -= h

        # Goods produced is given per annum
        nodes.loc[node, 'Local Value'] += h
        value_profit = (calculate_value(nodes)['My Value'].sum() - value) / (12 * h)
        nodes.loc[node, 'Local Value'] -= h

        marginal_profits.loc[node] = [power_profit, privateer_profit, value_profit]

    idx = marginal_profits['dct / power'].idxmax()
    print(f"Best profit from trade power {marginal_profits.loc[idx, 'dct / power']:.3} dct at {idx}")
    idx = marginal_profits['dct / privateer'].idxmax()
    print(f"Best profit from privateering {marginal_profits.loc[idx, 'dct / privateer']:.3f} dct at {idx}")
    idx = marginal_profits['dct / value'].idxmax()
    print(f"Best profit from trade value {marginal_profits.loc[idx, 'dct / value']:.3f} dct at {idx}")

if __name__ == '__main__':
    main()