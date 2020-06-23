# import numpy as np  # linear algebra
# import pandas as pd  # data processing, CSV file I/O (e.g. pd.read_csv)
import collections
import os
from minizinc import Instance, Model, Solver
import csv
from IPython.display import FileLink

def submission_generation(filename, str_output):
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        for item in str_output:
            writer.writerow(item)
    return FileLink(filename)


def check_solution(node_count, edges, solution):
    for edge in edges:
        if solution[edge[0]] == solution[edge[1]]:
            print("solución inválida, dos nodos adyacentes tienen el mismo color")
            return 0
    value = max(solution) + 1  # add one because minimum color is 0

    return value


def initializeMinizinc(maximo, edges, edge_count, node_count):
    # Create a MiniZinc model
    model = Model()

    model.add_string("""
            include "globals.mzn";
            int: e;
            int: n;
            int: m;
            set of int: nodes = 0..m;
            array[1..e, 1..2] of int: edges;
            array[0..n] of var nodes: Des;
                            
            var nodes: colors;
                            
            constraint Des[0] == 0;
            constraint forall(i in 1..e)(Des[edges[i,1]] != Des[edges[i,2]]);
            constraint forall(x, y in 0..n where y = x+1)(value_precede(x, y, Des) /\ 
            Des[y] <= colors);
            
            solve minimize colors;
            """)

    # Transform Model into a instance
    gecode = Solver.lookup("gecode")
    inst = Instance(gecode, model)
    inst["e"] = edge_count
    inst["n"] = node_count
    inst["m"] = maximo
    inst["edges"] = edges

    # Solve the instance
    result = inst.solve()
    return result["Des"]


def initializeMinizinc2(edges, edge_count, node_count):
    # Create a MiniZinc model
    model = Model()

    model.add_string("""
            include "globals.mzn";

            int: n;
            int: e;
            set of int: nodes;
            array[1..e, 1..2] of int: edges;
            array[0..n] of var nodes: Des;
            
            constraint forall(i in 1..e)(Des[edges[i,1]] != Des[edges[i,2]]);

            solve :: int_search(Des, most_constrained, indomain_min) satisfy;
            """)

    # Transform Model into a instance
    gecode = Solver.lookup("gecode")
    inst = Instance(gecode, model)
    inst["e"] = edge_count
    inst["n"] = node_count
    inst["nodes"] = range(0, node_count)
    inst["edges"] = edges

    # Solve the instance
    result = inst.solve()
    return result["Des"]


def solve_it(input_data):
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

    if edge_count <= 1200:
        freq = collections.Counter(t[0] for t in edges)
        maximo = max(freq.values()) + 1
        solution = initializeMinizinc(maximo, edges, edge_count, node_count - 1)
    else:
        solution = initializeMinizinc2(edges, edge_count, node_count - 1)

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

    submission_generation('Grupo1_ColoreadoDeGrafos.csv', str_output)
