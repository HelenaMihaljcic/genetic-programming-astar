
#python -m pytest tests/gp_test.py -v u root folderu
#potrebno je otkomentarisati linije u kojima ima import .imefoldera a zakomentarisati import imefoldera (gp_engine.py i a_star.py)
#NE RADI DRUGACIJE

import math
from unittest.mock import MagicMock, patch

import pytest

from core.gp_engine import (
    GPEngineThread,
    protected_div,
    pset,
    toolbox,
)


 
# protected_div
 

def test_protected_div_normal_division():
    assert protected_div(10.0, 2.0) == 5.0


def test_protected_div_zero_denominator():
    assert protected_div(10.0, 0.0) == 1.0


def test_protected_div_near_zero_denominator():
    assert protected_div(10.0, 0.0001) == 1.0


def test_protected_div_negative_near_zero_denominator():
    assert protected_div(10.0, -0.0001) == 1.0


def test_protected_div_negative_values():
    assert protected_div(-10.0, 2.0) == -5.0


 
# DEAP primitive set
 

def test_pset_has_expected_arguments():
    assert pset.arguments == [
        "dx",
        "dy",
        "d_manhattan",
        "d_euclidean",
        "obs_density",
    ]


def test_pset_return_type():
    assert pset.ret is float


def test_toolbox_can_generate_individual():
    individual = toolbox.individual()

    assert individual is not None
    assert len(individual) > 0
    assert individual.height >= 0


def test_toolbox_can_compile_individual():
    individual = toolbox.individual()
    func = toolbox.compile(expr=individual)

    result = func(
        1.0,
        2.0,
        3.0,
        math.sqrt(5.0),
        0.2,
    )

    assert isinstance(result, (int, float))


 
# Fixtures
 

@pytest.fixture
def mock_grid():
    grid = MagicMock()

    grid.start = (0, 0)
    grid.goal = (4, 4)

    grid.copy.return_value = grid
    grid.get_obstacle_density.return_value = 0.25

    return grid


@pytest.fixture
def engine(mock_grid):
    fake_path = [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0)]
    fake_visited = {(0, 0), (1, 0), (2, 0), (3, 0), (4, 0)}

    with patch(
        "core.gp_engine.run_a_star",
        return_value=(fake_path, fake_visited, None),
    ):
        engine = GPEngineThread(
            mock_grid,
            pop_size=10,
            ngen=5,
            cxpb=0.7,
            mutpb=0.2,
        )

    return engine


 
# GPEngineThread initialization
 

def test_engine_initialization(engine, mock_grid):
    assert engine.pop_size == 10
    assert engine.ngen == 5
    assert engine.cxpb == 0.7
    assert engine.mutpb == 0.2

    assert engine._is_paused is False
    assert engine._is_stopped is False

    assert engine.optimal_length == 5


def test_engine_copies_grid(mock_grid):
    with patch(
        "core.gp_engine.run_a_star",
        return_value=(
            [(0, 0), (1, 0)],
            {(0, 0)},
            None,
        ),
    ):
        GPEngineThread(
            mock_grid,
            pop_size=5,
            ngen=2,
            cxpb=0.5,
            mutpb=0.1,
        )

    mock_grid.copy.assert_called_once()


 
# Pause / resume / stop
 

def test_pause(engine):
    assert engine._is_paused is False

    engine.pause()

    assert engine._is_paused is True


def test_resume(engine):
    engine.pause()
    assert engine._is_paused is True

    engine.resume()

    assert engine._is_paused is False


def test_stop(engine):
    assert engine._is_stopped is False

    engine.stop()

    assert engine._is_stopped is True


 
# evaluate()
 

def test_evaluate_returns_tuple(engine):
    individual = toolbox.individual()

    with patch(
        "core.gp_engine.run_a_star",
        return_value=(
            [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0)],
            {(0, 0), (1, 0), (2, 0)},
            None,
        ),
    ):
        fitness = engine.evaluate(individual)

    assert isinstance(fitness, tuple)
    assert len(fitness) == 1
    assert isinstance(fitness[0], float)


def test_evaluate_with_simple_heuristic(engine):
    individual = toolbox.clone(
        toolbox.individual()
    )

    with patch(
        "core.gp_engine.run_a_star",
        return_value=(
            [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0)],
            {(0, 0), (1, 0)},
            None,
        ),
    ):
        fitness = engine.evaluate(individual)

    assert math.isfinite(fitness[0])


def test_evaluate_penalizes_missing_path(engine):
    individual = toolbox.individual()

    with patch(
        "core.gp_engine.run_a_star",
        return_value=([], set(), None),
    ):
        fitness = engine.evaluate(individual)

    assert fitness[0] < 0


def test_evaluate_penalizes_invalid_compilation(engine):
    invalid_individual = MagicMock()

    with patch(
        "core.gp_engine.toolbox.compile",
        side_effect=Exception("compile error"),
    ):
        fitness = engine.evaluate(invalid_individual)

    assert fitness == (-100000.0,)


def test_evaluate_handles_invalid_heuristic_result(engine):
    individual = toolbox.individual()

    def fake_a_star(grid, start, goal, heuristic):
        value = heuristic(0, 0, 4, 4, grid)

        assert value >= 0 or value == 10000.0

        return (
            [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0)],
            {(0, 0)},
            None,
        )

    with patch(
        "core.gp_engine.run_a_star",
        side_effect=fake_a_star,
    ):
        fitness = engine.evaluate(individual)

    assert isinstance(fitness, tuple)
    assert math.isfinite(fitness[0])


 
# emit_stats()
 

def test_emit_stats(engine):
    population = toolbox.population(n=3)

    for individual in population:
        individual.fitness.values = (float(-10),)

    hof = MagicMock()
    hof.__getitem__.return_value = population[0]

    received = []

    engine.generation_done.connect(
        lambda gen, best, avg, individual, expr:
        received.append(
            (gen, best, avg, individual, expr)
        )
    )

    engine.emit_stats(3, population, hof)

    assert len(received) == 1

    gen, best, avg, individual, expr = received[0]

    assert gen == 3
    assert best == -10.0
    assert avg == -10.0
    assert individual is population[0]
    assert isinstance(expr, str)


 
# run()
 

def test_run_stops_immediately_when_requested(engine):
    engine._is_stopped = True

    with patch.object(engine, "emit_stats") as emit_stats:
        with patch(
            "core.gp_engine.toolbox.population",
            return_value=[],
        ):
            engine.run()

    emit_stats.assert_called_once()

    assert emit_stats.call_args.args[0] == 0


def test_run_creates_population_and_evolves(engine):
    population = toolbox.population(n=4)

    with patch(
        "core.gp_engine.toolbox.population",
        return_value=population,
    ), patch.object(
        engine,
        "evaluate",
        return_value=(-10.0,),
    ), patch.object(
        engine,
        "emit_stats",
    ) as emit_stats:

        engine.ngen = 2
        engine.run()

    assert emit_stats.call_count == 3


def test_run_emits_evolution_finished(engine):
    population = toolbox.population(n=4)

    finished = []

    engine.evolution_finished.connect(
        lambda: finished.append(True)
    )

    with patch(
        "core.gp_engine.toolbox.population",
        return_value=population,
    ), patch.object(
        engine,
        "evaluate",
        return_value=(-10.0,),
    ), patch.object(
        engine,
        "emit_stats",
    ):

        engine.ngen = 0
        engine.run()

    assert finished == [True]