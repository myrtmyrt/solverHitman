from heapq import heappush, heappop
from math import fabs
from pprint import pprint
from typing import Dict, Callable, List, Tuple
from collections import deque, defaultdict, namedtuple
from hitman import HC, HitmanReferee, world_example

Variable = int
Literal = int
Clause = List[Literal]
Model = List[Literal]
Clause_Base = List[Clause]
Map = List[List[int]]
from typing import List, Tuple, Dict

# world_example_tuple = tuple(tuple(line) for line in world_example)
# pprint(world_example_tuple)
