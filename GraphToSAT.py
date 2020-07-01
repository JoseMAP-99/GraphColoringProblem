import collections
import time
import pymzn
from IPython.display import FileLink
import os
import csv
from itertools import combinations
from Functions.MultiSAT import execute
from multiprocessing import Process, Queue


def submission_generation(filename, str_output):
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        for item in str_output:
            writer.writerow(item)
    return FileLink(filename)


def check_solution(edges, solution):
    for edge in edges:
        if solution[edge[0]] == solution[edge[1]]:
            print("solución inválida, dos nodos adyacentes tienen el mismo color")
            return 0
    value = max(solution) + 1
    return value


def type1(edges, color):
    """
    Tipo 1 -> nColor * nEdges --> 2 * 3 = 6 claúsulas
    (!0_0 + !1_0), (!0_1 + !1_1)
    (!1_0 + !2_0), (!1_1 + !2_1)
    (!1_0 + !3_0), (!1_1 + !3_1)
    """

    clausulas = ""

    for i, f in edges:
        for x in range(0, color):
            clausulas += "(!" + str(i) + "_" + str(x) + "+!" + str(f) + "_" + str(x) + "),"
    return clausulas[:-1]


def type2(nodes, color):
    """
    Tipo 2 -> 4 nodos --> 4 claúsulas
    (0_0 + 0_1)
    (1_0 + 1_1)
    (2_0 + 2_1)
    (3_0 + 3_1)
    """

    clausulas = ""
    for n in range(0, nodes):
        clausulas += "("
        for x in range(0, color):
            clausulas += str(n) + "_" + str(x) + "+"
        clausulas = clausulas[:-1] + "),"
    return clausulas[:-1]


def type3(nodes, color):
    """
    Tipo 3 -> nColor * nNodes --> 3 * 4 = 12 claúsulas
    (!0_0 + !0_1), (!0_0 + !0_2), (!0_1 + !0_2)
    (!1_0 + !1_1), (!1_0 + !1_2), (!1_1 + !1_2)
    (!2_0 + !2_1), (!2_0 + !3_2), (!2_1 + !2_2)
    (!3_0 + !3_1), (!3_0 + !3_2), (!3_1 + !3_2)
    """

    clausulas = ""
    if color > 2:
        for n in range(0, nodes):
            for x, y in combinations(range(0, color - 1), 2):
                clausulas += "(!" + str(n) + "_" + str(x) + "+!" + str(n) + "_" + str(y) + "),"
    else:
        for n in range(0, nodes):
            clausulas += "(!" + str(n) + "_0+!" + str(n) + "_1),"

    return clausulas[:-1]


def getTypes(edges, node_count, color):
    """
        Tipo 1 -> nColor*nEdges --> 2*3=6 claúsulas
            (!0_0 + !1_0), (!0_1 + !1_1)
            (!1_0 + !2_0), (!1_1 + !2_1)
            (!1_0 + !3_0), (!1_1 + !3_1)
        Tipo 2 -> 4 nodos --> 4 claúsulas
            (0_0 + 0_1)
            (1_0 + 1_1)
            (2_0 + 2_1)
            (3_0 + 3_1)
        Tipo 3 -> nColor*nNodes --> 2*4=8 claúsulas
            (!0_0 + !0_1)
            (!1_0 + !1_1)
            (!2_0 + !2_1)
            (!3_0 + !3_1)
        14 clausulas
    """
    clType = type1(edges, color) + "," + type2(node_count, color) + "," + type3(node_count, color)

    return clType


def passMzn(path, edge_count):
    string = """
        include "globals.mzn";
        int: e;
        int: n;
        int: m;
        set of int: nodes = 0..m;
        array[1..e, 1..2] of int: edges;
        array[0..n] of var nodes: Des;
        
        constraint forall(i in 1..e)(Des[edges[i,1]] != Des[edges[i,2]]);  
        """
    if edge_count > 1200:
        string += "solve :: int_search(Des, most_constrained, indomain_min) satisfy;"
    else:
        string += """
        constraint forall(x, y in 0..n where y = x+1)(value_precede(x, y, Des));
            
        solve minimize max(Des);
        """
    with open(path, "w") as file:
        file.write(string)

    return path


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

    freq = collections.Counter(t[0] for t in edges)
    maximo = max(freq.values()) + 1

    a = pymzn.minizinc(passMzn("./graphcoloring2.mzn", edge_count), data={'e': edge_count,
                                                                          'n': node_count - 1,
                                                                          'm': maximo,
                                                                          'edges': edges})

    taken = list(a[0].get('Des').values())
    solution = check_solution(edges, taken)

        if edge_count > 1200:
        resU = True
        dictResU = {}
        upperColor = solution - 1
        cont = 0

        start = time.time()
        acc = 0
        while resU:
            print(resU)
            print(solution, upperColor)

            cl = getTypes(edges, node_count, upperColor)

            print("aqui")
            que = Queue()
            t = Process(target=execute, args=(cl, que,))
            t.start()
            t.join(timeout=100)

            if t.is_alive():
                t.kill()
                t.join()

            if not que.empty():
                ax = que.get()
                resU = ax[0]
                dictR = ax[1]
            else:
                resU = False
                dictR = None

            print("aca")

            if dictR:
                dictResU = dictR

            upperColor -= 1
            cont += 1
            end = time.time()
            acc += end-start
            print(acc)

        if cont > 1:
            taken = [0] * node_count
            for key, value in dictResU.items():
                if value:
                    aux = key.split("_")
                    taken[int(aux[0])] = int(aux[1])
            solution = check_solution(edges, taken)

    # build a trivial solution
    # every node has its own color

    # prepare the solution in the specified output format
    output_data = str(node_count) + ' ' + str(0) + '\n'
    output_data += ' '.join(map(str, taken))

    return output_data, solution


def main():
    for dirname, _, filenames in os.walk('./data'):
        for filename in filenames:
            print(os.path.join(dirname, filename))

    str_output = [["Filename", "Min_value"]]

    for dirname, _, filenames in os.walk('./data'):
        for filename in filenames:
            full_name = dirname + '/' + filename
            with open(full_name, 'r') as input_data_file:
                input_data = input_data_file.read()
                output, value = solve_it(input_data)
                str_output.append([filename, str(value)])
            print(filename, value)

    sortedlist = sorted(str_output, key=lambda row: row[0], reverse=False)
    submission_generation('SAT.csv', sortedlist)


if __name__ == '__main__':
    main()
