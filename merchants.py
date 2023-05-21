from nodes import calculate_value, read_nodes, place_merchants

def main():
    nodes = read_nodes()
    value = calculate_value(nodes)['My Value'].sum()
    print(f'Current profit: {value:.3f} dct')

    nodes = place_merchants(nodes)
    value = calculate_value(nodes)['My Value'].sum()
    print(f'Optimized profit: {value:.3f} dct')

if __name__ == '__main__':
    main()
