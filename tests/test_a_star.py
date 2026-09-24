
from core.grid import Grid
from core.a_star import (
    run_a_star,
    heuristic_manhattan,
    heuristic_euclidean,
    heuristic_dijkstra,
)


def print_grid(grid, path=None):
    path = set(path or [])

    for x in range(grid.size):
        row = ""

        for y in range(grid.size):
            if (x, y) == grid.start:
                row += "S "
            elif (x, y) == grid.goal:
                row += "G "
            elif (x, y) in path:
                row += "* "
            elif grid.is_wall(x, y):
                row += "# "
            else:
                row += ". "

        print(row)


def run_test(grid, name):
    start = grid.start
    goal = grid.goal

    heuristics = [
        ("Manhattan", heuristic_manhattan),
        ("Euclidean", heuristic_euclidean),
        ("Dijkstra", heuristic_dijkstra),
    ]

    print(f"\n{'=' * 50}")
    print(name)
    print(f"{'=' * 50}")

    print("\nGrid:")
    print_grid(grid)

    for heuristic_name, heuristic in heuristics:
        path, visited, execution_time = run_a_star(
            grid,
            start,
            goal,
            heuristic
        )

        print(f"\n--- {heuristic_name} ---")

        if path:
            print("Put:")
            print_grid(grid, path)

            print(f"Dužina puta: {len(path)}")
            print(f"Posjećenih čvorova: {len(visited)}")
            print(f"Vrijeme: {execution_time:.4f} ms")
        else:
            print("Put nije pronađen.")

        assert path != []
        assert path[0] == start
        assert path[-1] == goal

        for node in path:
            assert not grid.is_wall(*node)


def test_without_walls():
    grid = Grid(5)

    run_test(
        grid,
        "TEST 1 - BEZ ZIDOVA"
    )


def test_with_walls():
    grid = Grid(5)

    walls = [
        (1, 1),
        (1, 2),
        (1, 3),
        (2, 3),
        (3, 3),
    ]

    for x, y in walls:
        grid.set_wall(x, y)

    run_test(
        grid,
        "TEST 2 - SA ZIDOVIMA"
    )


if __name__ == "__main__":
    test_without_walls()
    test_with_walls()
