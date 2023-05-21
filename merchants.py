from nodes import calculate_value, read_nodes, remove_merchant, add_merchant
from sys import stderr

# Attempts to optimize home node with static merchant placement
# Takes as input the dataframe of nodes, returns best home node as string
def optimize_home(nodes):
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
    return best_home

# Attempt to optimize merchant placement using a greedy algorithm
# Takes as input the DataFrame of nodes and amount of merchants to place, returns optimized DataFrame
def place_merchants(nodes, merchants):
    nodes = nodes.copy()

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

def main():
    nodes = read_nodes()
    value = calculate_value(nodes)['My Value'].sum()
    print(f'Current profit: {value:.3f} dct')

    # First remove and count all merchants
    merchants = 0
    for node in nodes[nodes['Merchant']].index:
        remove_merchant(nodes, node)
        merchants += 1
    nodes['Collecting'] = False

    best_home = optimize_home(nodes)
    print(f'Best home node: {best_home}')
    nodes.loc[best_home, 'Collecting'] = True

    nodes = place_merchants(nodes, merchants)
    value = calculate_value(nodes)['My Value'].sum()
    print(f'Optimized profit: {value:.3f} dct')

if __name__ == '__main__':
    main()
