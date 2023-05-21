import pandas as pd
import sys

sys.path.append("../src")
from nodes import calculate_value, read_nodes

# Finds marginal profits from global modifiers using two-point derivative
# Takes as input DataFrame of nodes, value to compare against and step size h
# Returns marginal profits from 1% of trade efficiency, trade steering and power modifier as a tuple
def find_global_marginals(nodes, value, h):
    nodes['Trade Efficiency'] += h
    trade_eff = (calculate_value(nodes)['My Value'].sum() - value) / (100 * h)
    nodes['Trade Efficiency'] -= h
    nodes['Steering Bonus'] += h
    trade_steering = (calculate_value(nodes)['My Value'].sum() - value) / (100 * h)
    nodes['Steering Bonus'] -= h
    nodes['Power Modifier'] += h
    power_modifier = (calculate_value(nodes)['My Value'].sum() - value) / (100 * h)
    nodes['Power Modifier'] -= h

    return (trade_eff, trade_steering, power_modifier)

# Finds Marginal profits from trade power and value using two-point derivative
# Takes as input DataFrame of nodes, value to compare against and step size h
# Returns marginal profits as a DataFrame
def find_marginals(nodes, value, h):
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
    
    return marginal_profits

def main():
    nodes = read_nodes()
    nodes2 = calculate_value(nodes)
    print(nodes2.loc[nodes['Local Value'] > 0].to_string(), file=sys.stderr)
    print('', file=sys.stderr)
    value = nodes2['My Value'].sum()
    print(f'Current profit: {value:.3f} dct')

    trade_eff, trade_steering, power_modifier = find_global_marginals(nodes, value, 0.001)

    print('Marginal profit:')
    print(f"1% trade efficiency gives {trade_eff:.3f} dct")
    print(f"1% trade steering gives {trade_steering:.3f} dct")
    print(f"1% global trade power gives {power_modifier:.3f} dct")

    marginal_profits = find_marginals(nodes, value, 0.001)
    print(marginal_profits, file=sys.stderr)

    idx = marginal_profits['dct / power'].idxmax()
    print(f"Best profit from trade power {marginal_profits.loc[idx, 'dct / power']:.3} dct at {idx}")
    idx = marginal_profits['dct / value'].idxmax()
    print(f"Best profit from trade value {marginal_profits.loc[idx, 'dct / value']:.3f} dct at {idx}")

if __name__ == '__main__':
    main()