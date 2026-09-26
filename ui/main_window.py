from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QGridLayout, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QSpinBox, QDoubleSpinBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QGroupBox
)
from typing import Optional

from core.grid import Grid
from core.gp_engine import GPEngineThread
from ui.canvas_grid import CanvasGrid
from ui.tree_viewer import TreeViewer
from ui.charts import FitnessChart
from utils.evaluator import evaluate_heuristics


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("VisualGP-AStar: 3-Way Heuristic Comparison")
        self.resize(1600, 900)

        self.grid_size = 20
        self.grid_obj = Grid(self.grid_size)
        self.gp_thread: Optional[GPEngineThread] = None
        self.best_individual = None

        self._init_ui()

    def _init_ui(self) -> None:
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QGridLayout(central_widget)



        #manhattan grid
        group_m = QGroupBox("Manhattan Heuristic")
        l_m = QVBoxLayout(group_m)
        self.canvas_manhattan = CanvasGrid(self.grid_obj)
        l_m.addWidget(self.canvas_manhattan)
        main_layout.addWidget(group_m, 0, 0)

        #euclidean grid
        group_e = QGroupBox("Euclidean Heuristic")
        l_e = QVBoxLayout(group_e)
        self.canvas_euclidean = CanvasGrid(self.grid_obj)
        l_e.addWidget(self.canvas_euclidean)
        main_layout.addWidget(group_e, 0, 1)

        #evolved
        group_gp = QGroupBox("GP Evolved Heuristic")
        l_gp = QVBoxLayout(group_gp)
        self.canvas_gp = CanvasGrid(self.grid_obj)
        l_gp.addWidget(self.canvas_gp)
        main_layout.addWidget(group_gp, 0, 2)


        self.canvas_manhattan.grid_updated.connect(self.on_grid_interacted)
        self.canvas_euclidean.grid_updated.connect(self.on_grid_interacted)
        self.canvas_gp.grid_updated.connect(self.on_grid_interacted)




        controls_group = QGroupBox("Map & GP Controls")
        controls_layout = QVBoxLayout(controls_group)

        # dugma za generisanje Mape
        btn_layout = QHBoxLayout()
        btn_random10 = QPushButton("Map (10%)")
        btn_random20 = QPushButton("Map (20%)")
        btn_random30 = QPushButton("Map (30%)")
        btn_clear = QPushButton("Clear Map")

        btn_random10.clicked.connect(lambda: self.randomize_map(0.1))
        btn_random20.clicked.connect(lambda: self.randomize_map(0.2))
        btn_random30.clicked.connect(lambda: self.randomize_map(0.3))
        btn_clear.clicked.connect(lambda: self.randomize_map(0.0))

        btn_layout.addWidget(btn_random10)
        btn_layout.addWidget(btn_random20)
        btn_layout.addWidget(btn_random30)
        btn_layout.addWidget(btn_clear)
        controls_layout.addLayout(btn_layout)

        # forma za parametre
        form_layout = QGridLayout()
        form_layout.addWidget(QLabel("Population:"), 0, 0)
        self.spin_pop = QSpinBox()
        self.spin_pop.setRange(10, 1000)
        self.spin_pop.setValue(50)
        form_layout.addWidget(self.spin_pop, 0, 1)

        form_layout.addWidget(QLabel("Generations:"), 0, 2)
        self.spin_gen = QSpinBox()
        self.spin_gen.setRange(1, 500)
        self.spin_gen.setValue(50)
        form_layout.addWidget(self.spin_gen, 0, 3)

        form_layout.addWidget(QLabel("Crossover Rate:"), 1, 0)
        self.spin_cxpb = QDoubleSpinBox()
        self.spin_cxpb.setRange(0.0, 1.0)
        self.spin_cxpb.setValue(0.7)
        self.spin_cxpb.setSingleStep(0.1)
        form_layout.addWidget(self.spin_cxpb, 1, 1)

        form_layout.addWidget(QLabel("Mutation Rate:"), 1, 2)
        self.spin_mutpb = QDoubleSpinBox()
        self.spin_mutpb.setRange(0.0, 1.0)
        self.spin_mutpb.setValue(0.2)
        self.spin_mutpb.setSingleStep(0.1)
        form_layout.addWidget(self.spin_mutpb, 1, 3)

        controls_layout.addLayout(form_layout)

        # kontrole
        play_layout = QHBoxLayout()
        self.btn_start = QPushButton("Start Evolution")
        self.btn_pause = QPushButton("Pause")
        self.btn_compare = QPushButton("Compare & Animate All")
        self.btn_start.clicked.connect(self.toggle_evolution)
        self.btn_pause.clicked.connect(self.toggle_pause)
        self.btn_pause.setEnabled(False)
        self.btn_compare.clicked.connect(self.run_comparison)

        play_layout.addWidget(self.btn_start)
        play_layout.addWidget(self.btn_pause)
        play_layout.addWidget(self.btn_compare)
        controls_layout.addLayout(play_layout)

        self.lbl_expr = QLabel("Best Expression: None")
        self.lbl_expr.setWordWrap(True)
        controls_layout.addWidget(self.lbl_expr)

        # rezultati
        self.table_comp = QTableWidget(3, 4)
        self.table_comp.setHorizontalHeaderLabels(["Heuristic", "Visited", "Length", "Time (ms)"])
        self.table_comp.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_comp.verticalHeader().setVisible(False)
        self.table_comp.setItem(0, 0, QTableWidgetItem("Manhattan"))
        self.table_comp.setItem(1, 0, QTableWidgetItem("Euclidean"))
        self.table_comp.setItem(2, 0, QTableWidgetItem("GP Evolved"))
        controls_layout.addWidget(self.table_comp)

        main_layout.addWidget(controls_group, 1, 0)


        tree_group = QGroupBox("Evolved Tree")
        tree_layout = QVBoxLayout(tree_group)
        self.tree_viewer = TreeViewer()
        tree_layout.addWidget(self.tree_viewer)
        main_layout.addWidget(tree_group, 1, 1)

        #chart
        chart_group = QGroupBox("Evolution Charts")
        chart_layout = QVBoxLayout(chart_group)
        self.chart = FitnessChart()
        chart_layout.addWidget(self.chart)
        main_layout.addWidget(chart_group, 1, 2)


        main_layout.setRowStretch(0, 3)
        main_layout.setRowStretch(1, 2)


        main_layout.setColumnStretch(0, 1)
        main_layout.setColumnStretch(1, 1)
        main_layout.setColumnStretch(2, 1)

    def on_grid_interacted(self) -> None:
        self.canvas_manhattan.clear_visualization()
        self.canvas_euclidean.clear_visualization()
        self.canvas_gp.clear_visualization()

    def randomize_map(self, density: float) -> None:
        if self.gp_thread and self.gp_thread.isRunning():
            return
        self.grid_obj.randomize(density)
        self.canvas_manhattan.set_grid(self.grid_obj)
        self.canvas_euclidean.set_grid(self.grid_obj)
        self.canvas_gp.set_grid(self.grid_obj)

    def toggle_evolution(self) -> None:
        if self.gp_thread and self.gp_thread.isRunning():
            self.gp_thread.stop()
            self.gp_thread.wait()
            self.btn_start.setText("Start Evolution")
            self.btn_pause.setEnabled(False)
        else:
            self.chart.clear_chart()
            self.best_individual = None
            self.lbl_expr.setText("Best Expression: Computing...")
            self.on_grid_interacted()

            self.gp_thread = GPEngineThread(
                self.grid_obj,
                self.spin_pop.value(),
                self.spin_gen.value(),
                self.spin_cxpb.value(),
                self.spin_mutpb.value()
            )
            self.gp_thread.generation_done.connect(self.on_generation_done)
            self.gp_thread.evolution_finished.connect(self.on_evolution_finished)

            self.gp_thread.start()
            self.btn_start.setText("Stop Evolution")
            self.btn_pause.setText("Pause")
            self.btn_pause.setEnabled(True)

    def toggle_pause(self) -> None:
        if not self.gp_thread:
            return

        if self.gp_thread._is_paused:
            self.gp_thread.resume()
            self.btn_pause.setText("Pause")
        else:
            self.gp_thread.pause()
            self.btn_pause.setText("Resume")

    def on_generation_done(self, gen: int, best_fit: float, avg_fit: float, best_ind: any, best_expr: str) -> None:
        self.chart.add_data(gen, best_fit, avg_fit)
        self.lbl_expr.setText(f"Gen {gen} Best Expression: {best_expr}")
        self.best_individual = best_ind
        if gen % 5 == 0 or gen == self.spin_gen.value():
            self.tree_viewer.update_tree(best_ind)

    def on_evolution_finished(self) -> None:
        self.btn_start.setText("Start Evolution")
        self.btn_pause.setEnabled(False)
        self.run_comparison()

    def run_comparison(self) -> None:
        if not self.best_individual:
            return

        stats = evaluate_heuristics(self.grid_obj, self.best_individual)

        row = 0
        for name in ["Manhattan", "Euclidean", "GP Evolved"]:
            if name in stats:
                data = stats[name]
                self.table_comp.setItem(row, 1, QTableWidgetItem(str(data['visited'])))
                length_str = str(data['path_length']) if data['path_exists'] else "No Path"
                self.table_comp.setItem(row, 2, QTableWidgetItem(length_str))
                self.table_comp.setItem(row, 3, QTableWidgetItem(f"{data['time_ms']:.2f}"))
            row += 1

        if 'Manhattan' in stats and stats['Manhattan']['path_exists']:
            self.canvas_manhattan.show_a_star_results(
                stats['Manhattan']['visited_set'], stats['Manhattan']['path'], animate=True)

        if 'Euclidean' in stats and stats['Euclidean']['path_exists']:
            self.canvas_euclidean.show_a_star_results(
                stats['Euclidean']['visited_set'], stats['Euclidean']['path'], animate=True)

        if 'GP Evolved' in stats and stats['GP Evolved']['path_exists']:
            self.canvas_gp.show_a_star_results(
                stats['GP Evolved']['visited_set'], stats['GP Evolved']['path'], animate=True)