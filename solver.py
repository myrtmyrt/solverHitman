from pprint import pprint
from typing import Dict, Callable, List
from collections import deque, namedtuple
from hitman.hitman import HitmanReferee, HC, world_example
from collections import defaultdict
import time
from heapq import heappop, heappush

_State = namedtuple(
    "State",
    [
        "status",
        "phase",
        "guard_count",
        "civil_count",
        "m",
        "n",
        "position",
        "orientation",
        "has_weapon",
        "has_suit",
        "suit_on",
        "is_target_down",
        "world",
        "cost",
    ],
)


class State(_State):
    def __hash__(self):
        return hash(
            (
                self.position,
                self.orientation,
                self.has_weapon,
                self.has_suit,
                self.suit_on,
                self.is_target_down,
            )
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


def start_phase2() -> State:
    state = State(
        status="OK",
        phase=2,
        position=(0, 0),
        orientation=HC.N,
        has_weapon=False,
        has_suit=False,
        suit_on=False,
        is_target_down=False,
        world=world_example_tuple,
        cost=0,
    )
    return state


def update_world_content(state: State, x: int, y: int, new_content: HC) -> State:
    world = list(list(line) for line in state.world)  # convert
    world[m(state) - y - 1][x] = new_content  # update content
    new_state = state._replace(world=tuple(tuple(line) for line in world))  # convert
    return new_state


def kill_target(state: State) -> State:
    if state.phase != 2:
        raise ValueError("Err: invalid phase")

    x, y = state.position
    if get_world_content(state, x, y) != HC.TARGET or not state.has_weapon:
        return state._replace(status="Err: invalid move")

    new_state = state._replace(is_target_down=True)
    update_world_content(new_state, x, y, HC.EMPTY)

    return new_state


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


def neutralize_guard(state: State) -> State:
    if state.phase != 2:
        raise ValueError("Err: invalid phase")

    offset_x, offset_y = get_offset(state)
    x, y = state.position

    if get_world_content(state, x + offset_x, y + offset_y) not in [
        HC.GUARD_N,
        HC.GUARD_E,
        HC.GUARD_S,
        HC.GUARD_W,
    ] or (x, y) in [
        pos for (pos, _) in compute_guards(state)[(x + offset_x, y + offset_y)]
    ]:
        return state._replace(status="Err: invalid move")
    new_state = state._replace()
    update_world_content(new_state, x + offset_x, y + offset_y, HC.EMPTY)

    return new_state


def neutralize_civil(state: State) -> State:
    if state.phase != 2:
        raise ValueError("Err: invalid phase")

    offset_x, offset_y = get_offset(state)
    x, y = state.position
    if get_world_content(state, x + offset_x, y + offset_y) not in [
        HC.CIVIL_N,
        HC.CIVIL_E,
        HC.CIVIL_S,
        HC.CIVIL_W,
    ] or (x, y) in [
        pos for (pos, _) in compute_civils(state)[(x + offset_x, y + offset_y)]
    ]:
        return state._replace(status="Err: invalid move")

    new_state = state._replace()
    update_world_content(new_state, x + offset_x, y + offset_y, HC.EMPTY)

    return new_state


# def neutralize_civil(state: State) -> State:
#     if state.phase != 2:
#         raise ValueError("Err: invalid phase")
#
#     offset_x, offset_y = get_offset(state)
#     x, y = state.position
#     target_x = x + offset_x
#     target_y = y + offset_y
#
#     target_content = get_world_content(state, target_x, target_y)
#
#     if (
#         target_content != HC.CIVIL_N
#         and target_content != HC.CIVIL_S
#         and target_content != HC.CIVIL_E
#         and target_content != HC.CIVIL_W
#     ):
#         return state._replace(status="Err: invalid target")
#
#     new_state = update_world_content(state, target_x, target_y, HC.EMPTY)
#     return new_state


def take_suit(state: State) -> State:
    if state.phase != 2:
        raise ValueError("Err: invalid phase")

    x, y = state.position
    if get_world_content(state, x, y) != HC.SUIT:
        return state._replace(status="Err: invalid move")

    new_state = state._replace(has_suit=True)
    update_world_content(new_state, x, y, HC.EMPTY)

    return new_state


def take_weapon(state: State) -> State:
    if state.phase != 2:
        raise ValueError("Err: invalid phase")

    x, y = state.position
    if get_world_content(state, x, y) != HC.PIANO_WIRE:
        return state._replace(status="Err: invalid move")

    new_state = state._replace(has_weapon=True)
    update_world_content(new_state, x, y, HC.EMPTY)

    return new_state


def put_on_suit(state: State) -> State:
    if state.phase != 2:
        raise ValueError("Err: invalid phase")

    if not state.has_suit:
        return state._replace(status="Err: invalid move")

    new_state = state._replace(suit_on=True)

    return new_state


def generate_list_actions(hr: HitmanReferee) -> Dict[str, Callable]:
    """
    generate list of actions given an instance of HitmanReferee
    :rtype: object
    :param hr: instance of HitmanReferee
    :return: dict containing in key names of each action and in value the corresponding method in the HitmanReferee
    """
    return {
        "move": hr.move,
        "turn_clockwise": hr.turn_clockwise,
        "turn_anti_clockwise": hr.turn_anti_clockwise,
        "kill_target": hr.kill_target,
        "neutralize_guard": hr.neutralize_civil,
        "neutralize_civil": hr.neutralize_civil,
        "take_suit": hr.take_suit,
        "take_weapon": hr.take_weapon,
        "put_on_suit": hr.put_on_suit,
    }


def dict_to_tuple(dict):
    return (
        dict["position"],
        dict["orientation"],
        dict["has_weapon"],
        dict["has_suit"],
        dict["is_target_down"],
    )


actions = {
    "move": move,
    "turn_clockwise": turn_clockwise,
    "turn_anti_clockwise": turn_anti_clockwise,
    "kill_target": kill_target,
    "neutralize_guard": neutralize_guard,
    "neutralize_civil": neutralize_civil,
    "take_suit": take_suit,
    "take_weapon": take_weapon,
    "put_on_suit": put_on_suit,
}


def search_bfs() -> Tuple[List[str], State]:
    frontier = deque()  # deque is BFS, stack is DFS, heap is A*
    visited = set()
    path = defaultdict(
        list
    )  # Utiliser defaultdict pour stocker les actions associées à chaque prédécesseur
    frontier.append(start_phase2())
    to_expand: State = frontier.pop()
    while not (to_expand.is_target_down and to_expand.position == (0, 0)):
        if to_expand not in visited:
            for action_name, action in actions.items():
                new_state = action(to_expand)
                if new_state.status == "OK":
                    path[new_state].append((action_name, to_expand))
                    frontier.append(new_state)
                    visited.add(to_expand)
        else:
            to_expand = frontier.pop()

    last_state = to_expand

    actions_to_do = []
    while to_expand != start_phase2():
        action, predecessor = path[to_expand][0]
        actions_to_do.append(action)
        to_expand = predecessor
    actions_to_do.reverse()

    return actions_to_do, last_state


def search_dfs() -> Tuple[List[str], State]:
    frontier = stack()  # deque is BFS, stack is DFS, heap is A*
    visited = set()
    path = defaultdict(
        list
    )  # Utiliser defaultdict pour stocker les actions associées à chaque prédécesseur
    frontier.append(start_phase2())
    to_expand: State = frontier.pop()
    while not (to_expand.is_target_down and to_expand.position == (0, 0)):
        if to_expand not in visited:
            for action_name, action in actions.items():
                new_state = action(to_expand)
                if new_state.status == "OK":
                    path[new_state].append((action_name, to_expand))
                    frontier.append(new_state)
                    visited.add(to_expand)
        else:
            to_expand = frontier.pop()

    last_state = to_expand

    actions_to_do = []
    while to_expand != start_phase2():
        action, predecessor = path[to_expand][0]
        actions_to_do.append(action)
        to_expand = predecessor
    actions_to_do.reverse()

    return actions_to_do, last_state


def manhattan_distance(position1: Tuple[int, int], position2: Tuple[int, int]) -> int:
    # Calculer la distance de Manhattan entre deux positions
    x1, y1 = position1
    x2, y2 = position2
    return int(fabs(x1 - x2) + fabs(y1 - y2))


def heuristic(state: State) -> int:
    if not state.has_weapon:
        weapon_distance = manhattan_distance(
            state.position, get_weapon_position(world_example)
        )
    else:
        weapon_distance = 0
    if not state.is_target_down:
        target_distance = manhattan_distance(
            state.position, get_target_position(world_example)
        )
    else:
        target_distance = 0
    return (
        weapon_distance + target_distance + manhattan_distance(state.position, (0, 0))
    )


def search_glouton() -> Tuple[List[str], State]:
    frontier = []  # deque is BFS, stack is DFS, heap is A*
    visited = set()
    path = defaultdict(
        list
    )  # Utiliser defaultdict pour stocker les actions associées à chaque prédécesseur
    start_state = start_phase2()
    heappush(
        frontier, (0, id(start_state), start_state)
    )  # heuristic value, id(state), state
    _, _, to_expand = heappop(frontier)
    while not (to_expand.is_target_down and to_expand.position == (0, 0)):
        if to_expand not in visited:
            for action_name, action in actions.items():
                new_state = action(to_expand)
                if new_state.status == "OK":
                    path[new_state].append((action_name, to_expand))
                    heappush(frontier, (heuristic(new_state), id(new_state), new_state))
                    visited.add(to_expand)
        else:
            _, _, to_expand = heappop(frontier)

    last_state = to_expand

    actions_done = []
    while to_expand != start_phase2():
        action, predecessor = path[to_expand][0]
        actions_done.append(action)
        to_expand = predecessor
    actions_done.reverse()

    return actions_done, last_state


def search_astar() -> Tuple[List[str], State]:
    frontier = []  # deque is BFS, stack is DFS, heap is A*
    visited = set()
    path = defaultdict(
        list
    )  # Utiliser defaultdict pour stocker les actions associées à chaque prédécesseur
    start_state = start_phase2()
    heappush(
        frontier, (0, id(start_state), start_state)
    )  # heuristic value, id(state), state
    _, _, to_expand = heappop(frontier)
    while not (to_expand.is_target_down and to_expand.position == (0, 0)):
        if to_expand not in visited:
            for action_name, action in actions.items():
                new_state = action(to_expand)
                if new_state.status == "OK":
                    path[new_state].append((action_name, to_expand))

                    heappush(frontier, (heuristic(new_state), id(new_state), new_state))
                    visited.add(to_expand)
        else:
            _, _, to_expand = heappop(frontier)

    last_state = to_expand

    actions_done = []
    while to_expand != start_phase2():
        action, predecessor = path[to_expand][0]
        actions_done.append(action)
        to_expand = predecessor
    actions_done.reverse()

    return actions_done, last_state


def get_target_position(map: List[List[str]]) -> Tuple[int, int]:
    for i in range(len(map)):
        for j in range(len(map[i])):
            if map[i][j] != HC.TARGET:
                continue
            return (i, j)


def get_weapon_position(map: List[List[str]]) -> Tuple[int, int]:
    for i in range(len(map)):
        for j in range(len(map[i])):
            if map[i][j] != HC.PIANO_WIRE:
                continue
            return (i, j)


def phase2_run(hr, actions):
    for action in actions:
        if action == "move":
            status = hr.move()
            # pprint(status)
        elif action == "turn_clockwise":
            status = hr.turn_clockwise()
            # pprint(status)
        elif action == "turn_anti_clockwise":
            status = hr.turn_anti_clockwise()
            # pprint(status)
        elif action == "neutralize_civil":
            status = hr.neutralize_civil()
            # pprint(status)
        elif action == "neutralize_guard":
            status = hr.neutralize_guard()
            # pprint(status)
        elif action == "take_suit":
            status = hr.take_suit()
            # pprint(status)
        elif action == "take_weapon":
            status = hr.take_weapon()
            # pprint(status)
        elif action == "kill_target":
            status = hr.kill_target()
            # pprint(status)


def main():
    t0 = time.time()
    actions_dfs, last_state_dfs = search_dfs()
    t1 = time.time()
    actions_bfs, last_state_bfs = search_bfs()
    t2 = time.time()
    actions_glouton, last_state_glouton = search_glouton()
    t3 = time.time()
    actions_astar, last_state_astar = search_astar()
    t4 = time.time()
    hr = HitmanReferee()
    hr.start_phase2()
    phase2_run(hr, actions_astar)
    _, score, _ = hr.end_phase2()

    # print(last_state)
    print(f"DFS: {len(actions_dfs)} actions in {round((t1-t0)*1000)}ms")
    print(f"BFS: {len(actions_bfs)} actions in {round((t2-t1)*1000)}ms")
    print(f"Glouton: {len(actions_glouton)} actions in {round((t3-t2)*1000)}ms")
    print(f"A*: {len(actions_astar)} actions in {round((t4-t3)*1000)}ms")

    pprint(score)


if __name__ == "__main__":
    start_time = time.time()
    main()
    end_time = time.time()
    execution_time = end_time - start_time
    print("Temps d'exécution :", execution_time, "secondes")
