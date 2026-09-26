import operator
import math
import random
import time
from typing import Any, Tuple
from PyQt6.QtCore import QThread, pyqtSignal

from deap import base, creator, tools, gp
from grid import Grid
from a_star import run_a_star, heuristic_dijkstra

#from .grid import Grid
#from .a_star import run_a_star, heuristic_dijkstra


def protected_div(left: float, right: float) -> float:
    if abs(right) < 0.001:
        return 1.0
    return left / right



if not hasattr(creator, "FitnessMax"):
    creator.create("FitnessMax", base.Fitness, weights=(1.0,))
    creator.create("Individual", gp.PrimitiveTree, fitness=creator.FitnessMax)

pset = gp.PrimitiveSetTyped("MAIN", [float] * 5, float)
pset.addPrimitive(operator.add, [float, float], float)
pset.addPrimitive(operator.sub, [float, float], float)
pset.addPrimitive(operator.mul, [float, float], float)
pset.addPrimitive(protected_div, [float, float], float)
pset.addPrimitive(min, [float, float], float)
pset.addPrimitive(max, [float, float], float)

pset.renameArguments(ARG0="dx")
pset.renameArguments(ARG1="dy")
pset.renameArguments(ARG2="d_manhattan")
pset.renameArguments(ARG3="d_euclidean")
pset.renameArguments(ARG4="obs_density")

toolbox = base.Toolbox()
toolbox.register("expr", gp.genHalfAndHalf, pset=pset, min_=1, max_=3)
toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.expr)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)
toolbox.register("compile", gp.compile, pset=pset)
toolbox.register("select", tools.selTournament, tournsize=3)
toolbox.register("mate", gp.cxOnePoint)
toolbox.register("expr_mut", gp.genFull, min_=0, max_=2)
toolbox.register("mutate", gp.mutUniform, expr=toolbox.expr_mut, pset=pset)

toolbox.decorate("mate", gp.staticLimit(key=operator.attrgetter("height"), max_value=7))
toolbox.decorate("mutate", gp.staticLimit(key=operator.attrgetter("height"), max_value=7))


class GPEngineThread(QThread):
    generation_done = pyqtSignal(int, float, float, object, str)
    evolution_finished = pyqtSignal()

    def __init__(self, grid: Grid, pop_size: int, ngen: int, cxpb: float, mutpb: float) -> None:
        super().__init__()
        self.grid = grid.copy()
        self.pop_size = pop_size
        self.ngen = ngen
        self.cxpb = cxpb
        self.mutpb = mutpb

        self._is_paused = False
        self._is_stopped = False

        
        opt_path, _, _ = run_a_star(self.grid, self.grid.start, self.grid.goal, heuristic_dijkstra)
        self.optimal_length = len(opt_path)

    def pause(self) -> None:
        self._is_paused = True

    def resume(self) -> None:
        self._is_paused = False

    def stop(self) -> None:
        self._is_stopped = True

    def evaluate(self, individual: Any) -> Tuple[float]:
        try:
            func = toolbox.compile(expr=individual)
        except Exception:
            return (-100000.0,)

        def h_wrapper(x: int, y: int, gx: int, gy: int, grid_obj: Grid) -> float:
            dx = float(abs(x - gx))
            dy = float(abs(y - gy))
            dm = dx + dy
            de = math.sqrt(dx ** 2 + dy ** 2)
            od = grid_obj.get_obstacle_density(x, y)

            try:
                val = func(dx, dy, dm, de, od)
                if math.isnan(val) or math.isinf(val):
                    return 10000.0
                return max(0.0, val)
            except Exception:
                return 10000.0

        path, visited, _ = run_a_star(self.grid, self.grid.start, self.grid.goal, h_wrapper)

        if not path:
            no_path_penalty = 1000.0
            path_len = 0.0
        else:
            no_path_penalty = 0.0
            path_len = float(len(path))

        visited_nodes = float(len(visited))
        tree_depth = float(individual.height)

        fitness = -((3.0 * visited_nodes) + (10.0 * abs(path_len - self.optimal_length)) + (
                    0.1 * tree_depth) + no_path_penalty)
        return (fitness,)

    def run(self) -> None:
        pop = toolbox.population(n=self.pop_size)
        hof = tools.HallOfFame(1)

        # Evaluate initial population
        for ind in pop:
            ind.fitness.values = self.evaluate(ind)

        hof.update(pop)
        self.emit_stats(0, pop, hof)

        for gen in range(1, self.ngen + 1):
            while self._is_paused and not self._is_stopped:
                time.sleep(0.1)

            if self._is_stopped:
                break

            offspring = toolbox.select(pop, len(pop))
            offspring = list(map(toolbox.clone, offspring))

            for child1, child2 in zip(offspring[::2], offspring[1::2]):
                if random.random() < self.cxpb:
                    toolbox.mate(child1, child2)
                    del child1.fitness.values
                    del child2.fitness.values

            for mutant in offspring:
                if random.random() < self.mutpb:
                    toolbox.mutate(mutant)
                    del mutant.fitness.values

            invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
            for ind in invalid_ind:
                ind.fitness.values = self.evaluate(ind)

            pop[:] = offspring
            hof.update(pop)

            self.emit_stats(gen, pop, hof)

        self.evolution_finished.emit()

    def emit_stats(self, gen: int, pop: list, hof: Any) -> None:
        fits = [ind.fitness.values[0] for ind in pop]
        avg_fit = sum(fits) / len(fits)
        best_fit = hof[0].fitness.values[0]
        best_expr = str(hof[0])
        self.generation_done.emit(gen, best_fit, avg_fit, hof[0], best_expr)