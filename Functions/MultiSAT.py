from Functions.ProcessFile import process


def parserFormula(formula):
    litDict = {}
    clauses = []

    cont = 1
    for cl in formula.split(','):
        auxC = []
        for a in cl[1:-1].split('+'):
            b = a.replace("!", "")
            if b not in litDict:
                litDict[b] = cont
                cont += 1
            auxC.append(litDict[b] if a[0] != "!" else -litDict[b])
        clauses.append(auxC)

    return litDict, clauses


def execute(nameFile):

    litDict, clauses = parserFormula(nameFile)
    value, dictS = process(clauses)

    if dictS:
        dictSol = dict(zip(litDict.keys(), dictS.values()))
    else:
        dictSol = None

    if value == "UNSATISFIABLE":
        return False, dictSol
    else:
        return True, dictSol



