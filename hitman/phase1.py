from pprint import pprint
from typing import Dict, Callable, List, Tuple
from collections import deque
from hitman import HC, HitmanReferee, complete_map_example


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
    }


world_example = [
    [HC.EMPTY, HC.EMPTY, HC.EMPTY, HC.SUIT, HC.GUARD_S, HC.WALL, HC.WALL],
    [HC.EMPTY, HC.WALL, HC.EMPTY, HC.EMPTY, HC.EMPTY, HC.EMPTY, HC.EMPTY],
    [HC.TARGET, HC.WALL, HC.EMPTY, HC.EMPTY, HC.EMPTY, HC.CIVIL_N, HC.EMPTY],
    [HC.WALL, HC.WALL, HC.EMPTY, HC.GUARD_E, HC.EMPTY, HC.CIVIL_E, HC.CIVIL_W],
    [HC.EMPTY, HC.EMPTY, HC.EMPTY, HC.EMPTY, HC.EMPTY, HC.EMPTY, HC.EMPTY],
    [HC.EMPTY, HC.EMPTY, HC.WALL, HC.WALL, HC.EMPTY, HC.PIANO_WIRE, HC.EMPTY],
]


def compare_dictionaries(dict1, dict2):
    # Vérification des ensembles de clés
    if set(dict1.keys()) != set(dict2.keys()):
        return False

    # Comparaison des valeurs
    for key, value in dict2.items():
        if dict1[key] != value:
            return False

    return True


def search(hr: HitmanReferee, map: Dict[Tuple[int, int], HC]) -> List[str]:
    actions = generate_list_actions(hr)
    frontier = deque()
    visited = set()
    frontier.append(hr.start_phase1())
    to_expand = frontier.pop()
    print(to_expand)
    while compare_dictionaries(map, complete_map_example):
        print("start of while")
        if str(to_expand) not in visited:
            print("expanding state")
            for action_name, action in actions.items():
                new_state = action()
                frontier.append(new_state)
        else:
            print("already visited state")
        to_expand = frontier.pop()
    print("finished phase 1")
    return to_expand


def main():
    hr = HitmanReferee()
    status = hr.start_phase1()
    pprint(status)
    empty_map = {key: " " for key in complete_map_example}
    # transformer en tuple le dico
    tuple_paires = tuple(sorted(empty_map.items()))
    # Hacher le tuple de paires clé-valeur
    hachage = hash(tuple_paires)
    print(hachage)
    search(hr, empty_map)
    _, score, history, true_map = hr.end_phase1()
    pprint(score)
    pprint(true_map)
    pprint(history)


# a chaque action faire fonction qui prend toutes les infos qu on a et nous donne des deductions
# a chaque fois action on ajoute

if __name__ == "__main__":
    main()
