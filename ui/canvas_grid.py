from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from typing import List, Tuple, Set
from core.grid import Grid


class CanvasGrid(QWidget):
    grid_updated = pyqtSignal()

    def __init__(self, grid: Grid) -> None:
        super().__init__()
        self.grid_obj = grid
        self.cell_size = 20
        self.setMinimumSize(self.grid_obj.size * self.cell_size, self.grid_obj.size * self.cell_size)

        self.visited: Set[Tuple[int, int]] = set()
        self.path: List[Tuple[int, int]] = []

        self.anim_visited: List[Tuple[int, int]] = []
        self.anim_path: List[Tuple[int, int]] = []
        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self._animate_step)
        self.anim_index = 0
        self.anim_mode = 0  # 0: idle, 1: drawing visited, 2: drawing path

    def set_grid(self, grid: Grid) -> None:
        self.grid_obj = grid
        self.clear_visualization()
        self.update()

    def clear_visualization(self) -> None:
        self.anim_timer.stop()
        self.visited.clear()
        self.path.clear()
        self.anim_visited.clear()
        self.anim_path.clear()
        self.anim_mode = 0
        self.update()

    def show_a_star_results(self, visited: Set[Tuple[int, int]], path: List[Tuple[int, int]],
                            animate: bool = True) -> None:
        self.clear_visualization()
        if animate:
            self.visited = visited.copy()
            self.path = path.copy()
            self.anim_visited = list(visited)
            self.anim_path = path
            self.anim_index = 0
            self.anim_mode = 1
            self.visited.clear()
            self.path.clear()
            self.anim_timer.start(5)
        else:
            self.visited = visited
            self.path = path
            self.update()

    def _animate_step(self) -> None:
        if self.anim_mode == 1:
            chunk = 10
            for _ in range(chunk):
                if self.anim_index < len(self.anim_visited):
                    self.visited.add(self.anim_visited[self.anim_index])
                    self.anim_index += 1
                else:
                    self.anim_mode = 2
                    self.anim_index = 0
                    break
        elif self.anim_mode == 2:
            if self.anim_index < len(self.anim_path):
                self.path.append(self.anim_path[self.anim_index])
                self.anim_index += 1
            else:
                self.anim_mode = 0
                self.anim_timer.stop()
        self.update()

    def mousePressEvent(self, event) -> None:
        self._handle_mouse(event)

    def mouseMoveEvent(self, event) -> None:
        if event.buttons() & Qt.MouseButton.LeftButton:
            self._handle_mouse(event)

    def _handle_mouse(self, event) -> None:
        x = event.pos().x() // self.cell_size
        y = event.pos().y() // self.cell_size
        if 0 <= x < self.grid_obj.size and 0 <= y < self.grid_obj.size:
            # Prevent overwriting Start/Goal
            if (x, y) != self.grid_obj.start and (x, y) != self.grid_obj.goal:
                self.grid_obj.set_wall(x, y, is_wall=True)
                self.clear_visualization()
                self.grid_updated.emit()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()
        self.cell_size = min(w, h) // self.grid_obj.size

        for x in range(self.grid_obj.size):
            for y in range(self.grid_obj.size):
                rect = (x * self.cell_size, y * self.cell_size, self.cell_size, self.cell_size)

                # Base color
                if (x, y) == self.grid_obj.start:
                    color = QColor("green")
                elif (x, y) == self.grid_obj.goal:
                    color = QColor("red")
                elif self.grid_obj.is_wall(x, y):
                    color = QColor("black")
                elif (x, y) in self.path:
                    color = QColor("yellow")
                elif (x, y) in self.visited:
                    color = QColor("lightblue")
                else:
                    color = QColor("white")

                painter.fillRect(*rect, color)
                painter.setPen(QPen(QColor(200, 200, 200)))
                painter.drawRect(*rect)