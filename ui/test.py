import sys
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtCore import QTimer

from core.grid import Grid
from ui.canvas_grid import CanvasGrid


app = QApplication(sys.argv)

grid = Grid(20)
canvas = CanvasGrid(grid)

window = QMainWindow()
window.setCentralWidget(canvas)
window.resize(600, 600)
window.show()



def test():
    visited = {
        (1, 2), (1, 3), (2, 3),
        (3, 3), (3, 4), (4, 4),
        (5, 4), (5, 5), (6, 5)
    }

    path = [
        (3, 3),
        (3, 4),
        (2, 4),
        (3, 4),
        (4, 4),
        (4, 5),
        (5, 5),
        (6, 5),
        (5, 5),
        (5, 6),
    ]

    canvas.show_a_star_results(
        visited=visited,
        path=path,
        animate=True
    )

QTimer.singleShot(500, test)

sys.exit(app.exec())