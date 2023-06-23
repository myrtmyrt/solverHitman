from heapq import heappush, heappop
from math import fabs
from pprint import pprint
from typing import Dict, Callable, List, Tuple
from collections import deque, defaultdict, namedtuple
from hitman import HC, HitmanReferee, world_example
import time
from phase1 import *

world_example_tuple = tuple(tuple(line) for line in world_example)

Variable = int
Literal = int
Clause = List[Literal]
Model = List[Literal]
Clause_Base = List[Clause]
Map = List[List[int]]
from typing import List, Tuple, Dict

world_example_tuple = tuple(tuple(line) for line in world_example)

_State = namedtuple(
    "State",
    [
        "status",
        "phase",
        "position",
        "orientation",
        "world",
        "cost",
        "guards",
        "civils",
        "has_guessed",
    ],
)


class State(_State):
    def __hash__(self):
        return hash((self.position, self.orientation, self.world, self.has_guessed))

    def __eq__(self, other):
        return all(
            (
                self.position == other.position,
                self.orientation == other.orientation,
                self.world == other.world,
                self.has_guessed == other.has_guessed,
            )
        )


def is_tuple_complete(world: Tuple[Tuple], nb_lignes, nb_colonnes) -> bool:
    return len(world) == nb_lignes * nb_colonnes


#
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


#
def get_world_content(map: Tuple[Tuple], x: int, y: int) -> int:
    if x >= 3 or x < 0 or y >= 5 or y < 0:
        return HC.WALL
    # return map[m(map) - y - 1][x]
    return map[x][y]


def m(map: (())) -> int:
    return len(map)


def n(map: (())) -> int:
    return len(map[0])


def move(state: State) -> State:
    offset_x, offset_y = get_offset(state)
    x, y = state.position

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

    # new_state = state._replace(cost=5 * seen_by_guard_num(state))
    new_state = state._replace(
        position=(x + offset_x, y + offset_y),
        cost=state.cost + 1 + 5 * seen_by_guard_num(state),
    )
    vision = get_vision(new_state)
    for pos, content in vision:
        update_world_vision(new_state, pos[0], pos[1], content)
    if is_tuple_complete(new_state.world):
        new_state = new_state._replace(has_guessed=True)
    return new_state


def turn_clockwise(state: State) -> State:
    if state.orientation == HC.N:
        orientation = HC.E
    elif state.orientation == HC.E:
        orientation = HC.S
    elif state.orientation == HC.S:
        orientation = HC.W
    else:
        orientation = HC.N

    new_state = state._replace(
        orientation=orientation,
        cost=state.cost + 1,
    )
    vision = get_vision(new_state, world_example_tuple)
    for pos, content in vision:
        update_world_vision(new_state, pos[0], pos[1], content)
    if is_tuple_complete(new_state.world):
        new_state = new_state._replace(has_guessed=True)
    return new_state


def turn_anti_clockwise(state: State) -> State:
    if state.orientation == HC.N:
        orientation = HC.W
    elif state.orientation == HC.E:
        orientation = HC.N
    elif state.orientation == HC.S:
        orientation = HC.E
    else:
        orientation = HC.S

    new_state = state._replace(
        orientation=orientation,
        cost=state.cost + 1,
    )
    vision = get_vision(new_state)
    for pos, content in vision:
        update_world_vision(new_state, pos[0], pos[1], content)
    if is_tuple_complete(new_state.world):
        new_state = new_state._replace(has_guessed=True)
    return new_state


def get_vision(
    state: State, map: Tuple[Tuple], dist: int = 3
) -> List[Tuple[Tuple[int, int], HC]]:
    offset_x, offset_y = get_offset(state)
    pos = state.position
    x, y = pos
    vision = []
    for _ in range(0, dist):
        pos = x + offset_x, y + offset_y
        x, y = pos
        if x >= n(state) or y >= m(state) or x < 0 or y < 0:
            break
        vision.append(
            (
                pos,
                get_world_content(
                    map,
                    x,
                    y,
                ),
            )
        )
        if vision[-1][1] != HC.EMPTY:
            break
    return vision


def start_phase1(nb_colonnes: int, nb_lignes: int) -> State:
    state = State(
        status="OK",
        phase=1,
        position=(0, 0),
        orientation=HC.N,
        world=(()),
        has_guessed=False,
        cost=0,
        guards={},
        civils={},
    )
    state = state._replace(guards=compute_guards(state))
    state = state._replace(civils=compute_civils(state))
    return state


def update_world_vision(state: State, x: int, y: int, new_content: HC) -> State:
    world = list(list(line) for line in state.world)  # convert
    world[m(state) - y - 1][x] = new_content  # update content
    new_state = state._replace(world=tuple(tuple(line) for line in world))  # convert
    return new_state


def seen_by_guard_num(state: State) -> int:
    count = 0
    x, y = state.position
    if get_world_content(state, x, y) not in [
        HC.CIVIL_N,
        HC.CIVIL_E,
        HC.CIVIL_S,
        HC.CIVIL_W,
    ]:
        for guard, vision in state.guards.items():
            # Note : un garde ne peut pas voir au dela d'un objet,
            # mais si Hitman est sur l'objet alors il voit Hitman
            count += (
                1 if len([0 for ((l, c), _) in vision if l == x and c == y]) > 0 else 0
            )
    return count


def seen_by_civil_num(state: State) -> int:
    count = 0
    x, y = state.position
    if get_world_content(state, x, y) not in [
        HC.CIVIL_N,
        HC.CIVIL_E,
        HC.CIVIL_S,
        HC.CIVIL_W,
    ]:
        for civil, vision in state.civils.items():
            # Note : un garde ne peut pas voir au dela d'un objet,
            # mais si Hitman est sur l'objet alors il voit Hitman
            count += (
                1 if len([0 for ((l, c), _) in vision if l == x and c == y]) > 0 else 0
            )
    else:
        count = 1
    return count


def get_guard_offset(guard):
    if guard == HC.GUARD_N:
        offset = 0, 1
    elif guard == HC.GUARD_E:
        offset = 1, 0
    elif guard == HC.GUARD_S:
        offset = 0, -1
    elif guard == HC.GUARD_W:
        offset = -1, 0

    return offset


def get_guard_vision(state: State, guard_x, guard_y, dist=2):
    guard = get_world_content(state, guard_x, guard_y)
    offset_x, offset_y = get_guard_offset(guard)
    pos = (guard_x, guard_y)
    x, y = pos
    vision = []
    for _ in range(0, dist):
        pos = x + offset_x, y + offset_y
        x, y = pos
        if x >= n(state) or y >= m(state) or x < 0 or y < 0:
            break
        vision.append((pos, get_world_content(state, x, y)))
        if vision[-1][1] != HC.EMPTY:
            break
    return vision


def compute_guards(
    state: State,
) -> Dict[Tuple[int, int], List[Tuple[Tuple[int, int], HC]]]:
    locations = {}
    for l_index, l in enumerate(state.world):
        for c_index, c in enumerate(l):
            if c == HC.GUARD_N or c == HC.GUARD_E or c == HC.GUARD_S or c == HC.GUARD_W:
                guard_x, guard_y = (c_index, m(state) - l_index - 1)
                locations[(guard_x, guard_y)] = get_guard_vision(
                    state, guard_x, guard_y
                )
    return locations


def get_civil_offset(civil):
    if civil == HC.CIVIL_N:
        offset = 0, 1
    elif civil == HC.CIVIL_E:
        offset = 1, 0
    elif civil == HC.CIVIL_S:
        offset = 0, -1
    elif civil == HC.CIVIL_W:
        offset = -1, 0

    return offset


def get_civil_vision(state: State, civil_x, civil_y):
    civil = get_world_content(state, civil_x, civil_y)
    offset_x, offset_y = get_civil_offset(civil)
    pos = (civil_x, civil_y)
    x, y = pos
    vision = [(pos, get_world_content(state, x, y))]

    pos = x + offset_x, y + offset_y
    x, y = pos
    if n(state) > x >= 0 and m(state) > y >= 0:
        vision.append((pos, get_world_content(state, x, y)))
    return vision


def compute_civils(
    state: State,
) -> Dict[Tuple[int, int], List[Tuple[Tuple[int, int], HC]]]:
    locations = {}
    for l_index, l in enumerate(state.world):
        for c_index, c in enumerate(l):
            if c == HC.CIVIL_N or c == HC.CIVIL_E or c == HC.CIVIL_S or c == HC.CIVIL_W:
                civil_x, civil_y = (c_index, m(state) - l_index - 1)
                locations[(civil_x, civil_y)] = get_civil_vision(
                    state, civil_x, civil_y
                )
    return locations


# renvoie le successeur direct selon le state et son orientation
def successeur(state: State) -> State:
    if state.orientation == HC.E:
        state.position = (state.position[0], state.position[1] + 1)
    elif state.orientation == HC.N:
        state.position = (state.position[0] + 1, state.position[1])
    elif state.orientation == HC.S:
        state.position = (state.position[0] - 1, state.position[1])
    elif state.orientation == HC.W:
        state.position = (state.position[0], state.position[1] - 1)

    if state[0] >= n(state) or state[0] <= 1 or state[1] >= m(state) or state[1] <= 0:
        succ_state = ()  # si succ_state dépasse index grille, renvoie tuple vide
    return state


def manhattan_distance(position1: Tuple[int, int], position2: Tuple[int, int]) -> int:
    # Calculer la distance de Manhattan entre deux positions
    x1, y1 = position1
    x2, y2 = position2
    return int(fabs(x1 - x2) + fabs(y1 - y2))


def heuristic(state: State) -> int:
    distance = manhattan_distance(state.position, (0, 0))
    return distance + manhattan_distance(state.position, (0, 0))


def search_astar(
    nb_lignes: int, nb_colonnes: int, map: world_example_tuple
) -> Tuple[List[str], State]:
    actions = {
        "move": move,
        "turn_clockwise": turn_clockwise,
        "turn_anti_clockwise": turn_anti_clockwise,
    }

    frontier = []  # deque is BFS, stack is DFS, heap is A*
    visited = set()
    path = defaultdict(
        list
    )  # Utiliser defaultdict pour stocker les actions associées à chaque prédécesseur
    start_state = start_phase1(nb_colonnes, nb_lignes)
    heappush(
        frontier, (0, id(start_state), start_state)
    )  # heuristic value, id(state), state
    _, _, to_expand = heappop(frontier)
    while not to_expand.has_guessed:
        if to_expand not in visited:
            for action_name, action in actions.items():
                new_state = action(to_expand)
                if new_state.status == "OK":
                    path[new_state].append((action_name, to_expand))
                    heappush(
                        frontier,
                        (
                            heuristic(new_state) + new_state.cost,
                            id(new_state),
                            new_state,
                        ),
                    )
                    visited.add(to_expand)
        elif frontier:
            _, _, to_expand = heappop(frontier)
        else:
            break

    last_state = to_expand

    actions_done = []
    while to_expand != start_phase1():
        action, predecessor = path[to_expand][0]
        actions_done.append(action)
        to_expand = predecessor
    actions_done.reverse()
    return actions_done, last_state


def main():
    actions = search_astar(3, 5, world_example_tuple)
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
