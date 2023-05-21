First, ensure you have a Python 3 environment with Numpy and Pandas installed.
Substitute whatever Python binary you're using for BIN, it's probably either python or python3.

Benchmarking:
BIN ../src/benchmark.py > benchmark.txt

Marginal profits:
BIN ../src/marginal_profit.py 1> marginals.txt 2> marginals_full.txt

Merchants:
BIN ../src/merchants.py 1> merchants.txt 2> home_nodes.txt
