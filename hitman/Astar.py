# // A* (star) Pathfinding
# // Initialiser les listes ouvertes et fermées
# laisser openList être une liste vide de nœuds
# laisser closedList être une liste vide de nœuds
# // Ajouter le nœud de départ
# ajouter le nœud de départ à openList (laisser f à zéro)
# // Boucler jusqu'à ce que vous trouviez la fin
# tant que openList n'est pas vide
#     // Obtenir le nœud actuel
#     laisser currentNode être le nœud ayant la valeur f la plus faible
#     supprimer currentNode de openList
#     ajouter currentNode à closedList
#     // Trouvé la destination
#     si currentNode est la destination
#         Félicitations ! Vous avez trouvé la fin ! Revenez en arrière pour obtenir le chemin
#     // Générer les enfants
#     laisser les enfants du currentNode être les nœuds adjacents
#
#     pour chaque enfant parmi les enfants
#         // L'enfant est dans closedList
#         si l'enfant est dans closedList
#             continuer au début de la boucle for
#         // Créer les valeurs f, g et h
#         enfant.g = currentNode.g + distance entre l'enfant et le nœud actuel
#         enfant.h = distance entre l'enfant et la fin
#         enfant.f = enfant.g + enfant.h
#         // L'enfant est déjà dans openList
#         si la position de l'enfant est dans les positions des nœuds de openList
#             si enfant.g est supérieur à g du nœud de openList
#                 continuer au début de la boucle for
#         // Ajouter l'enfant à openList
#         ajouter l'enfant à openList
from inspect import stack

# Listes vides : Grid[[]], path
# No = noeud départ
# Regarder si successeurs noeuds peuvent être satisifable en testant chaque possibilité d'état (garde, civil,...)
# on prend celui qui a le numero le plus petit (=empty) et on l'ajoute au path
# on regarde

from pprint import pprint
from typing import Dict, Callable, List, Tuple
from collections import deque, namedtuple, defaultdict
from hitman import HitmanReferee, HC, world_example
import time

Variable = int
Literal = int
Clause = List[Literal]
Model = List[Literal]
Clause_Base = List[Clause]
Map = List[List[int]]


State = namedtuple(
    "State",
    [
        "status",
        "phase",
        "position",
        "orientation",
        "world",
    ],
)


def get_offset(state: State) -> (int, int):
    """
    returns the offset corresponding to the player's orientation
    :param state: current state
    :return: offset
    """
    if state.orientation == HC.N:
        offset = 0, 1
    elif state.orientation == HC.E:
        offset = 1, 0
    elif state.orientation == HC.S:
        offset = 0, -1
    else:
        offset = -1, 0

    return offset


world_example_tuple = tuple(tuple(line) for line in world_example)


# def get_world_content(state: State, x: int, y: int):
#     if x > m(state) or x < 0 or y > n(state) or y < 0:
#         return HC.WALL
#     return state.world[len(state.world) - y - 1][x]


def get_world_content(state: State, x: int, y: int):
    if x >= n(state) or x < 0 or y >= m(state) or y < 0:
        return HC.WALL
    return state.world[m(state) - y - 1][x]


def m(state: State) -> int:
    return len(state.world)


def n(state: State) -> int:
    return len(state.world[0])


def move(state: State) -> State:
    offset_x, offset_y = get_offset(state)
    x, y = state.position
    # print("moving to x: ", x + offset_x, " y: ", y + offset_y)
    if get_world_content(state, x + offset_x, y + offset_y) not in [
        HC.EMPTY,
        HC.PIANO_WIRE,
        HC.CIVIL_N,
        HC.CIVIL_E,
        HC.CIVIL_S,
        HC.CIVIL_W,
        HC.SUIT,
        HC.TARGET,
    ]:
        return state._replace(status="Err: invalid move")

    return state._replace(position=(x + offset_x, y + offset_y))


def turn_clockwise(state: State) -> State:
    if state.orientation == HC.N:
        orientation = HC.E
    elif state.orientation == HC.E:
        orientation = HC.S
    elif state.orientation == HC.S:
        orientation = HC.W
    else:
        orientation = HC.N

    return state._replace(orientation=orientation)


def turn_anti_clockwise(state: State) -> State:
    if state.orientation == HC.N:
        orientation = HC.W
    elif state.orientation == HC.E:
        orientation = HC.N
    elif state.orientation == HC.S:
        orientation = HC.E
    else:
        orientation = HC.S
    return state._replace(orientation=orientation)


def start_phase1() -> State:
    state = State(
        status="OK",
        phase=1,
        position=(0, 0),
        orientation=HC.N,
        world=world_example_tuple,
    )
    return State


def update_world_content(state: State, x: int, y: int, new_content: HC) -> State:
    world = list(list(line) for line in state.world)  # convert
    world[m(state) - y - 1][x] = new_content  # update content
    new_state = state._replace(world=tuple(tuple(line) for line in world))  # convert
    return new_state


def is_grid_full(grid: Map) -> bool:
    for line in grid:
        for cell in line:
            if cell == -1:
                return False
    return True


# vérifier si case déjà remplie
def is_in_grid(grid: Map, i, j) -> bool:
    if grid[i][j] != -1:
        return True
    return False


def update_grid_content(grid: Map, x: int, y: int, new_content: int) -> Map:
    grid[x][y] = new_content  # update content
    return grid


def search(nb_lignes: int, nb_colonnes: int) -> List[Tuple[int, int]]:
    grid = [[-1] * nb_colonnes for _ in range(nb_lignes)]  # initialiser grid à -1
    actions = {
        "move": move,
        "turn_clockwise": turn_clockwise,
        "turn_anti_clockwise": turn_anti_clockwise,
    }
    frontier = deque()  # deque is BFS, stack is DFS, heap is A*
    path = defaultdict(
        list
    )  # Utiliser defaultdict pour stocker les actions associées à chaque prédécesseur
    frontier.append(start_phase1())
    to_expand: State = frontier.pop()
    while not is_grid_full(grid):
        if to_expand not in grid:
            for action_name, action in actions.items():
                new_state = action(to_expand)
                if new_state.status == "OK":
                    path[new_state].append((action_name, to_expand))
                    frontier.append(new_state)
                    # update grid
        else:
            to_expand = frontier.pop()

    last_state = to_expand

    actions = []
    while to_expand != start_phase1():
        action, predecessor = path[to_expand][0]
        actions.append(action)
        to_expand = predecessor
    actions.reverse()
    return actions


def main():
    actions = search(6, 7)
    pprint(actions)
    # hr = HitmanReferee()
    # status = hr.start_phase1()
    # phase1_run(hr, actions)
    # _, score, history = hr.end_phase1()
    # pprint(score)


if __name__ == "__main__":
    start_time = time.time()
    main()
    end_time = time.time()
    execution_time = end_time - start_time
    print("Temps d'exécution :", execution_time, "secondes")
