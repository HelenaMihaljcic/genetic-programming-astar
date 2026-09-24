import sys
from PyQt6.QtWidgets import QApplication
from tree_viewer import TreeViewer


class Test:
    pass


from deap import gp

original_graph = gp.graph

gp.graph = lambda individual: (
    [0, 1, 2, 3, 4],
    [(0, 1), (0, 2), (1, 3), (1, 4)],
    {
        0: "max",
        1: "+",
        2: "obs_density",
        3: "dx",
        4: "dy"
    }
)


app = QApplication(sys.argv)

viewer = TreeViewer()
viewer.setWindowTitle("Tree Viewer Test")
viewer.resize(800, 600)

viewer.update_tree(Test())

viewer.show()

sys.exit(app.exec())