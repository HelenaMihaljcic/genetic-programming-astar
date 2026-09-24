from PyQt6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from typing import List


class FitnessChart(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.figure = Figure()
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.layout.addWidget(self.canvas)
        self.ax = self.figure.add_subplot(111)

        self.generations: List[int] = []
        self.best_fitness: List[float] = []
        self.avg_fitness: List[float] = []

        self.line_best, = self.ax.plot([], [], label='Best Fitness', color='green')
        self.line_avg, = self.ax.plot([], [], label='Avg Fitness', color='orange')

        self.ax.set_title("Evolution Progress")
        self.ax.set_xlabel("Generation")
        self.ax.set_ylabel("Fitness (Negative)")
        self.ax.legend()
        self.ax.grid(True)

    def clear_chart(self) -> None:
        self.generations.clear()
        self.best_fitness.clear()
        self.avg_fitness.clear()
        self.line_best.set_data([], [])
        self.line_avg.set_data([], [])
        self.ax.relim()
        self.ax.autoscale_view()
        self.canvas.draw()

    def add_data(self, gen: int, best: float, avg: float) -> None:
        self.generations.append(gen)
        self.best_fitness.append(best)
        self.avg_fitness.append(avg)

        self.line_best.set_data(self.generations, self.best_fitness)
        self.line_avg.set_data(self.generations, self.avg_fitness)

        self.ax.relim()
        self.ax.autoscale_view()
        self.canvas.draw()