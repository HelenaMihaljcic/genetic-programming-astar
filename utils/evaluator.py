import math
from typing import Dict, Any
from core.grid import Grid
from core.a_star import run_a_star, heuristic_manhattan, heuristic_euclidean
from core.gp_engine import toolbox


def evaluate_heuristics(grid: Grid, best_individual: Any) -> Dict[str, Dict[str, Any]]:
    results = {}

    # manhattan
    path_m, vis_m, time_m = run_a_star(grid, grid.start, grid.goal, heuristic_manhattan)
    results['Manhattan'] = {
        'path_length': len(path_m),
        'visited': len(vis_m),
        'time_ms': time_m,
        'path_exists': len(path_m) > 0,
        'path': path_m,
        'visited_set': vis_m
    }

    # euclidean
    path_e, vis_e, time_e = run_a_star(grid, grid.start, grid.goal, heuristic_euclidean)
    results['Euclidean'] = {
        'path_length': len(path_e),
        'visited': len(vis_e),
        'time_ms': time_e,
        'path_exists': len(path_e) > 0,
        'path': path_e, 
        'visited_set': vis_e
    }

    # evolved
    if best_individual:
        try:
            func = toolbox.compile(expr=best_individual)

            def h_gp(x: int, y: int, gx: int, gy: int, grid_obj: Grid) -> float:
                dx = float(abs(x - gx))
                dy = float(abs(y - gy))
                dm = dx + dy
                de = math.sqrt(dx ** 2 + dy ** 2)
                od = grid_obj.get_obstacle_density(x, y)
                try:
                    val = func(dx, dy, dm, de, od)
                    return max(0.0, val) if not math.isnan(val) and not math.isinf(val) else 10000.0
                except Exception:
                    return 10000.0

            path_g, vis_g, time_g = run_a_star(grid, grid.start, grid.goal, h_gp)
            results['GP Evolved'] = {
                'path_length': len(path_g),
                'visited': len(vis_g),
                'time_ms': time_g,
                'path_exists': len(path_g) > 0,
                'path': path_g,
                'visited_set': vis_g
            }
        except Exception:
            pass

    return results