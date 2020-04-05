# Input data files are available in the "../input/" directory.
# For example, running this (by clicking run or pressing Shift+Enter) will list all files under the input directory
# import numpy as np  # linear algebra
# import pandas as pd  # data processing, CSV file I/O (e.g. pd.read_csv)
import os
from minizinc import Instance, Model, Solver
import csv
import collections
from IPython.display import FileLink


# Ahí hay ejemplos de uso de minizinc-Python
# https://minizinc-python.readthedocs.io/en/latest/


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


def initializeMinizinc(maximo, inicios, finales, edge_count, node_count):
    # Create a MiniZinc model
    model = Model()

    model.add_string("""
            include "globals.mzn";
            int: e;
            int: n;
            int: m;
            set of int: nodes = 0..m;
            array[1..e] of int: Inicio;
            array[1..e] of int: Final;
            array[0..n] of var nodes: Des;
            
            var nodes: colors;
                    
            constraint Des[0] == 0 /\ 
            forall(i in index_set(Inicio))(Des[Inicio[i]] != Des[Final[i]]) /\ 
            forall(x, y in index_set(Des) where y = x+1)(value_precede(x, y, Des)) /\ 
            max(Des) == colors;
            
            solve minimize colors;     
            """)

    # Transform Model into a instance
    gecode = Solver.lookup("gecode")
    inst = Instance(gecode, model)

    inst["e"] = edge_count
    inst["n"] = node_count - 1
    inst["m"] = maximo

    inst["Inicio"] = inicios
    inst["Final"] = finales

    # Solve the instance
    result = inst.solve()
    return result["Des"]


def solve_it(input_data):
    # Modify this code to run your optimization algorithm

    # parse the input
    lines = input_data.split('\n')

    first_line = lines[0].split()
    node_count = int(first_line[0])
    edge_count = int(first_line[1])

    edges = []
    inicio = []
    final = []
    for i in range(1, edge_count + 1):
        line = lines[i]
        parts = line.split()
        edges.append((int(parts[0]), int(parts[1])))
        inicio.append(int(parts[0]))
        final.append(int(parts[1]))

    freq = collections.Counter(inicio)

    if edge_count == (node_count * (node_count - 1) / 2):
        maximo = node_count
    else:
        maximo = max(freq.values()) + 1

    if edge_count < 1200:
        solution = initializeMinizinc(maximo, inicio, final, edge_count, node_count)
    else:
        solution = initializeMinizinc(maximo, inicio, final, edge_count, node_count)

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

    submission_generation('Grupo1_Provisional.csv', str_output)
