import collections
import pymzn
from IPython.display import FileLink
import os
import csv
from itertools import combinations
import subprocess
from networkx import algorithms, Graph


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
    clType = str(type1(edges, color)) + "," + str(type2(node_count, color)) + "," + str(type3(node_count, color))

    return clType


def parserFormula(formula):
    litDict = {}
    clauses = []

    cont = 1
    for cl in formula.split(','):
        auxC = ""
        for a in cl[1:-1].split('+'):
            b = a.replace("!", "")
            if b not in litDict:
                litDict[b] = cont
                cont += 1
            auxC += (str(litDict[b]) + " " if a[0] != "!" else str(-litDict[b]) + " ")
        clauses.append([auxC + "0"])

    return dict(zip(litDict.values(), litDict.keys())), clauses


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


def greedyColor(edgesX, node_countX):
    G = Graph()
    G.add_edges_from(edgesX)

    res = algorithms.coloring.greedy_color(G, strategy='independent_set')

    taken = [0] * node_countX
    for key, value in res.items():
        taken[key] = value
    return taken


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

    greedyColor(edges, node_count)

    if edge_count < 100000:

        freq = collections.Counter(t[0] for t in edges)
        maximo = max(freq.values()) + 1

        a = pymzn.minizinc(passMzn("./graphcoloring.mzn", edge_count), data={'e': edge_count,
                                                                             'n': node_count - 1,
                                                                             'm': maximo,
                                                                             'edges': edges})

        taken = list(a[0].get('Des').values())
        solution = check_solution(edges, taken)

        if edge_count > 1200:

            def createCNF():
                auxT = getTypes(edges, node_count, solution - 1)
                litDict, cnf = parserFormula(auxT)

                text = [["p cnf " + str(len(litDict.keys())) + " " + str(len(cnf))]]
                text.extend(cnf)
                name = "./CNF/n" + str(node_count) + "_e" + str(edge_count) + ".cnf"
                submission_generation(name, text)
                return name, litDict

            while True:
                nam, dictResU = createCNF()
                run = "./Sparrow2Riss-2018-fixfix/bin/SparrowToRiss.sh " + nam + " 1 ./Temp"
                process = subprocess.Popen(run.split(), stdout=subprocess.PIPE)
                try:
                    process.wait(timeout=30)
                except subprocess.TimeoutExpired:
                    try:
                        os.kill(process.pid, 0)
                    finally:
                        break
                output, error = process.communicate()
                if error:
                    print("Oh no! ERROR")
                    break
                res = output.decode("utf-8").split("\n")
                sat = True if res[-3] == "s SATISFIABLE" else False
                if not sat:
                    break
                sol = res[-2]
                vectSol = [int(x) for x in sol[1:-1].split()]

                taken = [0] * node_count
                for x in vectSol:
                    if x > 0:
                        aux = dictResU.get(x).split("_")
                        taken[int(aux[0])] = int(aux[1])
                solution = check_solution(edges, taken)
    else:
        taken = greedyColor(edges, node_count)
        solution = check_solution(edges, taken)

    # prepare the solution in the specified output format
    output_data = str(node_count) + ' ' + str(0) + '\n'
    output_data += ' '.join(map(str, taken))

    return output_data, solution


def main():
    conta = 0
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
            conta += 1
            print(filename, value, conta, "/36")

    sortedlist = sorted(str_output, key=lambda row: row[0], reverse=False)
    submission_generation('SAT.csv', sortedlist)


if __name__ == '__main__':
    main()
