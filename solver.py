from pprint import pprint
from typing import Dict, Callable, List
from collections import deque
from hitman.hitman import HitmanReferee


def generate_list_actions(hr: HitmanReferee) -> Dict[str, Callable]:
    """
    generate list of actions given an instance of HitmanReferee
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


def search(hr: HitmanReferee) -> List[str]:
    actions = generate_list_actions(hr)
    frontier = deque()
    visited = set()
    frontier.append(hr.start_phase2())
    to_expand = frontier.pop()
    print(to_expand)
    while not to_expand["has_weapon"]:
        print("start of while")
        if to_expand not in visited:
            print("expanding state")
            for action_name, action in actions.items():
                new_state = action()
                frontier.append(new_state)
        else:
            print("already visited state")
        to_expand = frontier.pop()
    print("has weapon")
    return to_expand
