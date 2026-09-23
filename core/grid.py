import numpy as np
import random
from typing import Tuple

class Grid:
    def __init__(self, size: int = 20) -> None:
        self.size = size
        self.grid = np.zeros((size, size), dtype=int)
        self.start: Tuple[int, int] = (0, 0)
        self.goal: Tuple[int, int] = (size - 1, size - 1)
        self.grid[self.start] = 0
        self.grid[self.goal] = 0

    def set_wall(self, x: int, y: int, is_wall: bool = True) -> None:
        if (x, y) == self.start or (x, y) == self.goal:
            return
        if 0 <= x < self.size and 0 <= y < self.size:
            self.grid[x, y] = 1 if is_wall else 0

    def toggle_wall(self, x: int, y: int) -> None:
        if (x, y) == self.start or (x, y) == self.goal:
            return
        if 0 <= x < self.size and 0 <= y < self.size:
            self.grid[x, y] = 1 - self.grid[x, y]

    def is_wall(self, x: int, y: int) -> bool:
        if 0 <= x < self.size and 0 <= y < self.size:
            return self.grid[x, y] == 1
        return True

    def randomize(self, density: float) -> None:
        self.grid = np.zeros((self.size, self.size), dtype=int)
        for x in range(self.size):
            for y in range(self.size):
                if (x, y) != self.start and (x, y) != self.goal:
                    if random.random() < density:
                        self.grid[x, y] = 1

    def get_obstacle_density(self, x: int, y: int) -> float:
        walls = 0
        total = 0
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.size and 0 <= ny < self.size:
                    total += 1
                    if self.grid[nx, ny] == 1:
                        walls += 1
        return walls / total if total > 0 else 0.0

    def copy(self) -> 'Grid':
        new_grid = Grid(self.size)
        new_grid.grid = np.copy(self.grid)
        new_grid.start = self.start
        new_grid.goal = self.goal
        return new_grid