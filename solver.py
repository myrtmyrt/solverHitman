from pprint import pprint
from typing import Dict, Callable, List
from collections import deque, namedtuple
from hitman.hitman import HitmanReferee, HC, complete_map_example, world_example

"""
state:
{
            "status": err,
            "phase": self.__phase,
            "guard_count": self.__guard_count,
            "civil_count": self.__civil_count,
            "m": self.__m,
            "n": self.__n,
            "position": self.__pos,
            "orientation": self.__orientation,
            "vision": self.__get_vision(),
            "hear": self.__get_listening(),
            "penalties": self.__phase1_penalties,
            "is_in_guard_range": self.__is_in_guard_range,
        }
"""
State = namedtuple(
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
        "vision",
        "hear",
        "is_in_guard_range",
    ],
)


def get_offset(state: State) -> (int, int):
    if state.orientation == HC.N:
        offset = 0, 1
    elif state.orientation == HC.E:
        offset = 1, 0
    elif state.orientation == HC.S:
        offset = 0, -1
    else:
        offset = -1, 0

    return offset


world = world_example


def get_world_content(x: int, y: int):
    # provisoire
    return world[len(world) - y - 1][x]


def move(state: State) -> State:
    offset_x, offset_y = get_offset(state)
    x, y = state.position
    if get_world_content(x + offset_x, y + offset_y) not in [
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
    state = State()
    state.phase = 2
    state.pos = (0, 0)
    state.orientation = HC.N
    return state


def end_phase2(state: State):
    if not state.is_target_down or not state.pos == (0, 0):
        return False, "Err: finish the mission and go back to (0,0)", []
    self.__phase = 0
    return True, f"Your score is {- self.__phase2_penalties}", self.__phase2_history


def kill_target(self):
    if self.__phase != 2:
        raise ValueError("Err: invalid phase")

    self.__add_history("Kill Target")
    x, y = self.__pos
    if self.__get_world_content(x, y) != HC.TARGET or not self.__has_weapon:
        return self.__get_status_phase_2("Err: invalid move")

    self.__update_world_content(x, y, HC.EMPTY)
    self.__is_target_down = True

    return self.__get_status_phase_2()


def neutralize_guard(self):
    if self.__phase != 2:
        raise ValueError("Err: invalid phase")

    self.__add_history("Neutralize Guard")
    self.__phase2_penalties += 1
    self.__phase2_penalties += 5 * self.__seen_by_guard_num()

    offset_x, offset_y = self.__get_offset()
    x, y = self.__pos

    if self.__get_world_content(x + offset_x, y + offset_y) not in [
        HC.GUARD_N,
        HC.GUARD_E,
        HC.GUARD_S,
        HC.GUARD_W,
    ] or (x, y) in [pos for (pos, _) in self.__guards[(x + offset_x, y + offset_y)]]:
        return self.__get_status_phase_2("Err: invalid move")

    self.__update_world_content(x + offset_x, y + offset_y, HC.EMPTY)
    self.__guard_count -= 1

    return self.__get_status_phase_2()


def neutralize_civil(self):
    if self.__phase != 2:
        raise ValueError("Err: invalid phase")

    self.__add_history("Neutralize Civil")

    offset_x, offset_y = self.__get_offset()
    x, y = self.__pos
    if self.__get_world_content(x + offset_x, y + offset_y) not in [
        HC.CIVIL_N,
        HC.CIVIL_E,
        HC.CIVIL_S,
        HC.CIVIL_W,
    ] or (x, y) in [pos for (pos, _) in self.__civils[(x + offset_x, y + offset_y)]]:
        return self.__get_status_phase_2("Err: invalid move")

    self.__update_world_content(x + offset_x, y + offset_y, HC.EMPTY)
    self.__civil_count -= 1

    return self.__get_status_phase_2()


def take_suit(self):
    if self.__phase != 2:
        raise ValueError("Err: invalid phase")

    self.__add_history("Take Suit")

    x, y = self.__pos
    if self.__get_world_content(x, y) != HC.SUIT:
        return self.__get_status_phase_2("Err: invalid move")

    self.__has_suit = True
    self.__update_world_content(x, y, HC.EMPTY)

    return self.__get_status_phase_2()


def take_weapon(self):
    if self.__phase != 2:
        raise ValueError("Err: invalid phase")

    x, y = self.__pos
    if self.__get_world_content(x, y) != HC.PIANO_WIRE:
        return self.__get_status_phase_2("Err: invalid move")

    self.__has_weapon = True
    self.__update_world_content(x, y, HC.EMPTY)

    return self.__get_status_phase_2()


def put_on_suit(self):
    if self.__phase != 2:
        raise ValueError("Err: invalid phase")

    if not self.__has_suit:
        return self.__get_status_phase_2("Err: invalid move")

    self.__suit_on = True

    return self.__get_status_phase_2()


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


def search(hr: HitmanReferee) -> List[str]:
    actions = generate_list_actions(hr)
    frontier = deque()
    visited = set()
    frontier.append(hr.start_phase2())
    to_expand = frontier.pop()
    print(to_expand)
    while not to_expand["has_weapon"]:
        to_expand_tuple = dict_to_tuple(to_expand)
        if to_expand_tuple not in visited:
            for action_name, action in actions.items():
                print("=== NEW ACTION ===")
                print(hr.__pos)
                hr.__pos = to_expand["position"]
                hr.__orientation = to_expand["orientation"]
                hr.__has_weapon = to_expand["has_weapon"]
                hr.__has_suit = to_expand["has_suit"]
                hr.__is_target_down = to_expand["is_target_down"]
                print(hr.__pos)
                new_state = action()
                print(hr.__pos)
                pprint(action_name)
                # pprint(new_state["position"])
                pprint(new_state["orientation"])
                pprint(new_state["status"])
                if new_state["status"] == "OK":
                    frontier.append(new_state)
                    visited.add(to_expand_tuple)
        else:
            to_expand = frontier.pop()
    print("has weapon")
    return to_expand


def main():
    hr = HitmanReferee()
    status = hr.start_phase2()  # Appeler start_phase2 sur l'instance hr
    # pprint(search(hr))
    search(hr)  # Passer l'instance hr à la fonction search
    pprint("fin : ")
    _, score, history = hr.end_phase2()  # Appeler end_phase2 sur l'instance hr
    pprint(score)
    pprint(history)


if __name__ == "__main__":
    main()
