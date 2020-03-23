# Input data files are available in the "../input/" directory.
# For example, running this (by clicking run or pressing Shift+Enter) will list all files under the input directory
#import numpy as np  # linear algebra
#import pandas as pd  # data processing, CSV file I/O (e.g. pd.read_csv)
import os
import minizinc

# Ahí hay ejemplos de uso de minizinc-Python
# https://minizinc-python.readthedocs.io/en/latest/


def check_solution(node_count, edges, solution):
    for edge in edges:
        if solution[edge[0]] == solution[edge[1]]:
            print("solución inválida, dos nodos adyacentes tienen el mismo color")
            return 0
    value = max(solution) + 1  # add one because minimum color is 0

    return value


def solve_it(input_data):
    # Modify this code to run your optimization algorithm

    # parse the input
    lines = input_data.split('\n')

    first_line = lines[0].split()
    node_count = int(first_line[0])
    edge_count = int(first_line[1])

    edges = []
    for i in range(1, edge_count + 1):
        line = lines[i]
        parts = line.split()
        edges.append((int(parts[0]), int(parts[1])))
    
    
    # Create a MiniZinc model
    model = minizinc.Model()
    model.add_string("""
    var -100..100: x;
    int: a; int: b; int: c;
    constraint a*(x*x) + b*x = c;
    solve satisfy;
    """)

    # Transform Model into a instance
    gecode = minizinc.Solver.lookup("gecode")
    inst = minizinc.Instance(gecode, model)
    inst["a"] = 1
    inst["b"] = 0
    inst["c"] = 4

    # Solve the instance
    result = inst.solve(all_solutions=True)
    for i in range(len(result)):
        print("x = {}".format(result[i, "x"]))

        
    # build a trivial solution
    # every node has its own color
    solution = range(0, node_count)

    # prepare the solution in the specified output format
    output_data = str(node_count) + ' ' + str(0) + '\n'
    output_data += ' '.join(map(str, solution))

    return output_data, check_solution(node_count, edges, solution)


if __name__ == "__main__":
    for dirname, _, filenames in os.walk('data'):
        for filename in filenames:
            print(os.path.join(dirname, filename))

    str_output = [["Filename", "Min_value"]]

    for dirname, _, filenames in os.walk('data'):
        for filename in filenames:
            full_name = dirname + '/' + filename
            with open(full_name, 'r') as input_data_file:
                input_data = input_data_file.read()
                output, value = solve_it(input_data)
                print(filename, value)
                str_output.append([filename, str(value)])
