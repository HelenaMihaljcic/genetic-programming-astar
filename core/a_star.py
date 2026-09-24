import heapq
import time
import math
from typing import Callable, Tuple, List, Set, Dict
from core.grid import Grid


def heuristic_manhattan(x: int, y: int, gx: int, gy: int, grid: Grid) -> float:
    return float(abs(x - gx) + abs(y - gy))


def heuristic_euclidean(x: int, y: int, gx: int, gy: int, grid: Grid) -> float:
    return math.sqrt((x - gx) ** 2 + (y - gy) ** 2)


def heuristic_dijkstra(x: int, y: int, gx: int, gy: int, grid: Grid) -> float:
    return 0.0


def run_a_star(
        grid: Grid,
        start: Tuple[int, int],
        goal: Tuple[int, int],
        heuristic_fn: Callable[[int, int, int, int, Grid], float]
) -> Tuple[List[Tuple[int, int]], Set[Tuple[int, int]], float]:
    """
    Returns: (path, visited_nodes, execution_time_ms)
    """
    start_time = time.perf_counter()

    open_set = []
    heapq.heappush(open_set, (0.0, start))

    came_from: Dict[Tuple[int, int], Tuple[int, int]] = {}
    g_score: Dict[Tuple[int, int], float] = {start: 0.0}

    visited: Set[Tuple[int, int]] = set()

    while open_set:
        _, current = heapq.heappop(open_set)

        visited.add(current)

        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            path.reverse()

            end_time = time.perf_counter()
            return path, visited, (end_time - start_time) * 1000.0

        x, y = current
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
            nx, ny = x + dx, y + dy

            if not (0 <= nx < grid.size and 0 <= ny < grid.size):
                continue
            if grid.is_wall(nx, ny):
                continue

            step_cost = 1.414 if dx != 0 and dy != 0 else 1.0
            tentative_g = g_score[current] + step_cost

            neighbor = (nx, ny)
            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                h_val = heuristic_fn(nx, ny, goal[0], goal[1], grid)
                if math.isnan(h_val) or math.isinf(h_val):
                    h_val = 10000.0
                f_score = tentative_g + h_val
                heapq.heappush(open_set, (f_score, neighbor))

    end_time = time.perf_counter()
    return [], visited, (end_time - start_time) * 1000.0