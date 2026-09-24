import sys
from PyQt6.QtWidgets import QApplication
from charts import FitnessChart


app = QApplication(sys.argv)

chart = FitnessChart()
chart.setWindowTitle("Fitness Chart Test")
chart.resize(800, 500)


data = [
    (0, -1500, -1800),
    (1, -1200, -1600),
    (2, -1000, -1400),
    (3, -850, -1200),
    (4, -700, -1050),
    (5, -600, -900),
    (6, -520, -800),
    (7, -450, -700),
    (8, -400, -620),
    (9, -350, -550),
]

for gen, best, avg in data:
    chart.add_data(gen, best, avg)

chart.show()

sys.exit(app.exec())