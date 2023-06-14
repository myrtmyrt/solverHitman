from typing import List, Tuple
import subprocess
from pprint import pprint
import itertools as iter
from hitman.hitman import HC,HitmanReferee

# Alias de types
Variable = int
Literal = int
Clause = List[Literal]
Model = List[Literal]
Clause_Base = List[Clause]
Map = List[List[int]]

nb_lignes= 5;
nb_colonnes=4;
nb_gardes=1;
nb_civil=2;
nb_clause=17*nb_colonnes*nb_lignes;

example: Map = [
    [3, 1, 1, 1, 12],
    [1, 2, 2, 1, 1],
    [1, 9, 1, 1, 1],
    [17, 8, 1, 1, 13],
]\

HitmanReferee.start_phase1()





