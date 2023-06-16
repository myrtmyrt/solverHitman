from typing import List, Tuple
import subprocess
from pprint import pprint
import itertools as iter
from hitman import HC, HitmanReferee, complete_map_example

# Alias de types
Variable = int
Literal = int
Clause = List[Literal]
Model = List[Literal]
Clause_Base = List[Clause]
Map = List[List[int]]

nb_lignes = 7
nb_colonnes = 6
nb_gardes = 1
nb_civil = 2
nb_etats = 13
nb_variables = 13 * nb_colonnes * nb_lignes

example: Map = [[1, 1, 2, 4], [2, 1, 1, 1], [1, 1, 12, 5], [1, 9, 13, 1], [15, 1, 1, 8]]


def write_dimacs_file(dimacs: str, filename: str):
    with open(filename, "w+", newline="") as cnf:
        cnf.write(dimacs)

#appel gophersat
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


# donne le numero de la variable correspondant à la case i,j et à l'état val
def cell_to_variable(i: int, j: int, val: int) -> int:
    return 13 * nb_colonnes * i + 13 * j + val


# passer de la variable au numéro de la case et à l'état
def variable_to_cell(var: int) -> Tuple[int, int, int]:
    var -= 1
    i = var // 91
    j = var % 91 // 13
    var = var % 91 % 13 + 1
    return (i, j, var)


# appliquer la contrainte unique (1 seul element unique par case)
def unique(vars: List[int]) -> List[List[int]]:
    r = []
    r.append(at_least_one(vars))
    for l in iter.combinations(vars, 2):
        l = [-x for x in l]
        r.append(l)
    return r


# passer de la liste de clauses au fichier dimacs
def clauses_to_dimacs(clauses: List[List[int]], nb_vars: int) -> str:
    o = f"p cnf {nb_vars} {len(clauses)}\n"
    for l in clauses:
        for x in l:
            o += f"{x} "
        o += "0\n"
    return o


# appliquer la contrainte au moins un (au moins un element par case)
def at_least_one(vars: List[int]) -> List[int]:
    return vars[:]


def unique(vars: List[int]) -> List[List[int]]:
    r = []
    r.append(at_least_one(vars))
    for l in iter.combinations(vars, 2):
        l = [-x for x in l]
        r.append(l)
    return r


def create_list_of_guards() -> List[int]:
    list = []
    sublist = []
    for i in range(nb_lignes):
        for j in range(nb_colonnes):
            sublist.append(cell_to_variable(i, j, HC.GUARD_E.value)),
            sublist.append(cell_to_variable(i, j, HC.GUARD_S.value)),
            sublist.append(cell_to_variable(i, j, HC.GUARD_W.value)),
            sublist.append(cell_to_variable(i, j, HC.GUARD_N.value)),
    for l in iter.combinations(sublist, 2):
        l = [-x for x in l]
        list.append(l)
    return list


# def create_guard_constraint() -> List[List[int]]:
#     list = []
#         for i in range(nb_lignes):
#             for j in range(nb_colonnes):
#                 #if Map[i][j] == HC.GUARD_N.value: # or Map[i][j] == HC.GUARD_S.value or Map[i][j] == HC.GUARD_E.value or Map[i][j] == HC.GUARD_W.value: other case can't be GUARD_N or GUARD_S or GUARD_E or GUARD_W


# def create_object_constraints() -> List[List[int]]:


def create_cell_constraints() -> List[List[int]]:
    list = []
    for j in range(nb_colonnes):
        for i in range(nb_lignes):
            raw = [
                x
                for x in range(
                    cell_to_variable(i, j, HC.EMPTY.value),
                    cell_to_variable(i, j, HC.PIANO_WIRE.value) + 1,
                )
            ]
            list += unique(raw)
    return list


def create_unique_constraints() -> List[List[int]]:
    result = []
    for j in range(nb_colonnes):
        for i in range(nb_lignes):
            sublist = []
            for val in range(nb_etats):
                sublist.append(cell_to_variable(i, j, val))
            result.append(sublist)
    return result


# create fonction to create unique personne for each

# def create_unique_personne(nb_personnes: int, rang_variable) -> List[List[int]]:
#     list = []
#     for l in nb_lignes:
#         for c in nb_colonnes:
#             for i in nb_variables:
#                 raw = [
#                     x
#                     for x in range(cell_to_variable(l, c, 3), cell_to_variable(l, c, 6))
#                 ]
#                 list += unique(raw)
#
#     return list


def generate_problem(grid: List[List[int]]) -> List[List[int]]:
    list = []
    list += create_cell_constraints()
    list += create_list_of_guards()
    # list += create_unique_personne(nb_gardes, 3)
    return list


def main():
    clauses = []
    clauses += generate_problem(Map)
    write_dimacs_file(
        clauses_to_dimacs(clauses, nb_colonnes * nb_lignes * nb_etats), "dimacs.cnf"
    )
    # clauses_to_dimacs(clauses, len(clauses))
    # res = exec_gophersat("dimacs.cnf", cmd="../gophersat")
    # print(res)


if __name__ == "__main__":
    main()
