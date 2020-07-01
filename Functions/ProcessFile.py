from Algos.CDCL import CDCL
from Algos.CP_SAT import ConstProg


def convertBool(values, ax):
    if ax < 0:
        au = -values[abs(ax) - 1]
    else:
        au = values[abs(ax) - 1]
    return True if au > 0 else False


def check_solution(values, clauses):
    sol = True
    for unit in clauses:
        aux = False
        for i in unit:
            aux = aux or convertBool(values, i)
        sol = sol and aux

    return "SATISFIABLE" if sol else "UNSATISFIABLE"


def process(clauses):
    cdcl = CDCL(clauses)
    cdcl.solve()
    val, dictSol = cdcl.sat, cdcl.satDict

    obj = "UNSATISFIABLE"

    if val:
        sol = [0] * len(dictSol)
        for key, value in dictSol.items():
            sol[abs(key) - 1] = abs(key) if value else -abs(key)

        obj = check_solution(sol, clauses)

    aux = True if obj == "SATISFIABLE" else False
    assert val == aux

    return obj, dictSol
