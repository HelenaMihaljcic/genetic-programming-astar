from PyQt6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import networkx as nx
from deap import gp
from typing import Any, Dict, Tuple


class TreeViewer(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.figure = Figure()
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.layout.addWidget(self.canvas)
        self.ax = self.figure.add_subplot(111)
        self.ax.axis("off")

    def _get_tree_layout(self, edges: list) -> Dict[int, Tuple[float, float]]:
        from collections import defaultdict
        children = defaultdict(list)
        for u, v in edges:
            children[u].append(v)

        pos = {}

        def assign_pos(node: int, depth: int, left: float, right: float) -> None:
            x = (left + right) / 2
            y = -depth
            pos[node] = (x, y)
            if children[node]:
                num_children = len(children[node])
                step = (right - left) / num_children
                for i, child in enumerate(children[node]):
                    assign_pos(child, depth + 1, left + i * step, left + (i + 1) * step)

        if len(edges) > 0 or True:
            # Determine root (node 0)
            assign_pos(0, 0, 0.0, 1.0)
        return pos

    def update_tree(self, individual: Any) -> None:
        self.ax.clear()
        self.ax.axis("off")

        if not individual:
            self.canvas.draw()
            return

        nodes, edges, labels = gp.graph(individual)

        g = nx.Graph()
        g.add_nodes_from(nodes)
        g.add_edges_from(edges)

        pos = self._get_tree_layout(edges)

        nx.draw_networkx_nodes(g, pos, ax=self.ax, node_size=600, node_color='lightgreen', edgecolors='black')
        nx.draw_networkx_edges(g, pos, ax=self.ax, arrows=False)
        nx.draw_networkx_labels(g, pos, labels, ax=self.ax, font_size=8)

        self.figure.tight_layout()
        self.canvas.draw()