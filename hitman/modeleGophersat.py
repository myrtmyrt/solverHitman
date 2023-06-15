from typing import List, Tuple
import subprocess
from pprint import pprint
import itertools as iter

# Alias de types
Variable = int
Literal = int
Clause = List[Literal]
Model = List[Literal]
Clause_Base = List[Clause]
Map = List[List[int]]

nb_lignes = 5
nb_colonnes = 4
nb_gardes = 1
nb_civil = 2
nb_clause = 17 * nb_colonnes * nb_lignes
vars = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]

example: Map = [
    [3, 1, 1, 1, 12],
    [1, 2, 2, 1, 1],
    [1, 9, 1, 1, 1],
    [17, 8, 1, 1, 13],
]


def write_dimacs_file(dimacs: str, filename: str):
    with open(filename, "w+", newline="") as cnf:
        cnf.write(dimacs)


def exec_gophersat(
    filename: str, cmd: str = "gophersat", encoding: str = "utf8"
) -> Tuple[bool, List[int]]:
    result = subprocess.run(
        [cmd, filename], capture_output=True, check=True, encoding=encoding
    )
    string = str(result.stdout)
    lines = string.splitlines()

    if lines[1] != "s SATISFIABLE":
        return False, []

    model = lines[2][2:].split(" ")

    return True, [int(x) for x in model]


def cell_to_variable(i: int, j: int, val: int) -> int:
    return nb_lignes * nb_colonnes * i + 17 * j + val


def unique(vars: List[int]) -> List[List[int]]:
    r = []
    r.append(at_least_one(vars))
    for l in iter.combinations(vars, 2):
        l = [-x for x in l]
        r.append(l)
    return r


def clauses_to_dimacs(clauses: List[List[int]], nb_vars: int) -> str:
    o = f"p cnf {nb_vars} {len(clauses)}\n"
    for l in clauses:
        for x in l:
            o += f"{x} "
        o += "0\n"
    return o


def at_least_one(vars: List[int]) -> List[int]:
    return vars[:]


def unique(vars: List[int]) -> List[List[int]]:
    r = []
    r.append(at_least_one(vars))
    for l in iter.combinations(vars, 2):
        l = [-x for x in l]
        r.append(l)
    return r


def create_unique_constraints() -> List[List[int]]:
    list = []
    for c in range(nb_lignes):
        for j in range(nb_colonnes):
            sublist = []
            for i in range(17):
                sublist.append(cell_to_variable(i, j, c))
            list.append(sublist)
    return list


def generate_problem(grid: List[List[int]]) -> List[List[int]]:
    list = []
    list += create_unique_constraints()
    return list


def main():
    vars = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
    clauses = unique(vars)
    clauses += generate_problem(Map)
    write_dimacs_file(clauses_to_dimacs(clauses, 340), "dimacs.cnf")
    # clauses_to_dimacs(clauses, len(clauses))
    res = exec_gophersat("dimacs.cnf", cmd="../gophersat")


if __name__ == "__main__":
    main()
