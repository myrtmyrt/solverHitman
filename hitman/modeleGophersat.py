from typing import List, Tuple
from enum import Enum
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

# variables à modifier
nb_lignes = 7
nb_colonnes = 6
nb_gardes = 1
nb_civil = 2
nb_etats = 13
nb_variables = 13 * nb_colonnes * nb_lignes

# exemple Map
example: Map = [[1, 1, 2, 4], [2, 1, 1, 1], [1, 1, 12, 5], [1, 9, 13, 1], [15, 1, 1, 8]]

#corbeille ->
#obtenir liste clauses unicité guardes
# def create_list_of_guards() -> List[int]:
#     list = []
#     sublist = []
#     for i in range(nb_lignes):
#         for j in range(nb_colonnes):
#             sublist.append(cell_to_variable(i, j, HC.GUARD_E.value)),
#             sublist.append(cell_to_variable(i, j, HC.GUARD_S.value)),
#             sublist.append(cell_to_variable(i, j, HC.GUARD_W.value)),
#             sublist.append(cell_to_variable(i, j, HC.GUARD_N.value)),
#     for l in iter.combinations(sublist, 2):
#         l = [-x for x in l]
#         list.append(l)
#     return list
# def guards_constraints(vars: List[int], n: int, i, j) -> List[int]:
#     complete_list = [[]]
#     at_least = []
#     i -= 2
#     j -= 2
#     if (i>= 6): i = 6
#     if (j == 7): j -= 2
#     for val in vars:
#         sublist = []
#         for i in range(i+2):
#             for j in range(j+2):
#                 sublist.append(cell_to_variable(i, j, val))
#                 complete_list.append(sublist)
#     #liste totale créée
#     #at_least
#     for k in range (len(complete_list)):
#         for h in range (len(complete_list[k])):
#             for g in range (len(complete_list[k+1])):
#                 for f in range (len(complete_list[k+2])):
#                     for t in range (len(complete_list[k+3])):
#                         sublist = [complete_list[k][h],complete_list[k+1][h],complete_list[k+2][h],complete_list[k+3][h]]
#                         at_least.append(sublist)
#
#     return at_least

##
class HN(Enum):
    EMPTY = 1
    WALL = 2
    GUARD = 3
    CIVIL = 4
    SUIT = 5
    PIANO_WIRE = 6


# permet de passer de la variable au numéro de la case
def cell_to_variable(i: int, j: int, val: int) -> int:
    return 5 * nb_colonnes * i + 5 * j + val

# passer de la variable au numéro de la case
def variable_to_cell(var: int) -> Tuple[int, int, int]:
    var -= 1
    i = var // (5*nb_colonnes)
    j = var % (5*nb_colonnes) // 5
    var = var % (5*nb_colonnes) % 5 + 1
    return (i, j, var)

# appliquer la contrainte au moins un (au moins un element par case)
def cell_at_least_one(vars: List[int]) -> List[int]:
    return vars[:]
# appliquer la contrainte unique (1 seul element unique par case)
def cell_unique(vars: List[int]) -> List[List[int]]:
    r = []
    r.append(cell_at_least_one(vars))
    for l in iter.combinations(vars, 2):
        l = [-x for x in l]
        r.append(l)
    return r
def create_cell_constraints() -> List[List[int]]:
    liste = []
    for i in range(nb_lignes):
        for j in range(nb_colonnes):
            raw = [
                x
                for x in range(cell_to_variable(i, j, HN.EMPTY.value), cell_to_variable(i, j, HN.PIANO_WIRE.value) + 1)
            ]
            liste += cell_unique(raw)
    return liste

def create_list_elt(element : int) -> List[int]:
    r_list = []
    for i in range(nb_lignes):
        for j in range(nb_colonnes):
            r_list.append(cell_to_variable(i, j, element))
    return r_list
def at_least_n(vars : List[int], n:int)-> List[Tuple[int]] :
    list = []
    for l in iter.combinations(vars, n):
        list.append(l)
    return list

def only_n(vars: List[int], n: int) -> List[List[int]]:
    list = []
    list.append(at_least_n(vars, n))
    for l in iter.combinations(vars, 2*n):
        l = [-x for x in l]
        list.append(l)
    return list
def create_person_constraint(person : int, n : int) -> List[List[int]]:
    list_person = create_list_elt(person)
    return only_n(list_person, n)

def create_object_constraints(object : int) -> List[List[int]]:
    list_object = create_list_elt(object)
    return only_n(list_object, 1)


# passer de la liste de clauses au fichier dimacs
def clauses_to_dimacs(clauses: List[List[int]], nb_vars: int) -> str:
    o = f"p cnf {nb_vars} {len(clauses)}\n"
    for l in clauses:
        for x in l:
            o += f"{x} "
        o += "0\n"
    return o
def write_dimacs_file(dimacs: str, filename: str):
    with open(filename, "w+", newline="") as cnf:
        cnf.write(dimacs)

# appel gophersat
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

def generate_problem() -> List[List[int]]:
    liste = []
    liste += create_cell_constraints()
    liste += create_object_constraints(HN.PIANO_WIRE.value)
    liste += create_object_constraints(HN.SUIT.value)
    liste += create_person_constraint(HN.GUARD.value,nb_gardes)
    liste += create_person_constraint(HN.CIVIL.value,nb_civil)
    return liste

def main():
    clauses = []
    clauses += generate_problem()
    write_dimacs_file(
        clauses_to_dimacs(clauses, nb_colonnes * nb_lignes * nb_etats), "dimacs.cnf"
    )

    #create_n_constraints(list(range(HC.GUARD_N.value,HC.GUARD_W.value)),4)
    # clauses_to_dimacs(clauses, len(clauses))
    # res = exec_gophersat("dimacs.cnf", cmd="../gophersat")
    # print(res)


if __name__ == "__main__":
    main()
