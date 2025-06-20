from typing import Dict, List, Tuple, Set
import heapq
import math


class Node:
    def __init__(self, position: Tuple[int, int], g_cost: float = float('inf'),
                 h_cost: float = 0, parent: 'Node' = None):
        self.position = position
        self.g_cost = g_cost
        self.h_cost = h_cost
        self.parent = parent

    @property
    def f_cost(self) -> float:
        return self.g_cost + self.h_cost

    def __lt__(self, other: 'Node') -> bool:
        return self.f_cost < other.f_cost


class AStar:
    def __init__(self):
        self.directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]

    def heuristic(self, start: Tuple[int, int], end: Tuple[int, int]) -> float:
        return abs(end[0] - start[0]) + abs(end[1] - start[1])

    def get_neighbors(self, current: Tuple[int, int], walkable_tiles: Set[Tuple[int, int]]) -> List[Tuple[int, int]]:
        neighbors = []
        for dx, dy in self.directions:
            neighbor = (current[0] + dx, current[1] + dy)
            if neighbor in walkable_tiles:
                neighbors.append(neighbor)
        return neighbors

    def find_path(self, start: Tuple[int, int], end: Tuple[int, int],
                  walkable_tiles: Set[Tuple[int, int]]) -> List[Tuple[int, int]]:
        if start not in walkable_tiles or end not in walkable_tiles:
            return []

        start_node = Node(start, g_cost=0, h_cost=self.heuristic(start, end))

        open_list: List[Node] = [start_node]
        closed_set: Set[Tuple[int, int]] = set()

        nodes: Dict[Tuple[int, int], Node] = {start: start_node}

        while open_list:
            current = heapq.heappop(open_list)

            if current.position == end:
                path = []
                while current:
                    path.append(current.position)
                    current = current.parent
                return path[::-1]

            closed_set.add(current.position)

            for neighbor_pos in self.get_neighbors(current.position, walkable_tiles):
                if neighbor_pos in closed_set:
                    continue

                g_cost = current.g_cost + 1

                if neighbor_pos not in nodes:
                    neighbor = Node(
                        neighbor_pos,
                        g_cost=g_cost,
                        h_cost=self.heuristic(neighbor_pos, end),
                        parent=current
                    )
                    nodes[neighbor_pos] = neighbor
                    heapq.heappush(open_list, neighbor)
                else:
                    neighbor = nodes[neighbor_pos]
                    if g_cost < neighbor.g_cost:
                        neighbor.g_cost = g_cost
                        neighbor.parent = current
                        if neighbor not in open_list:
                            heapq.heappush(open_list, neighbor)

        return []
