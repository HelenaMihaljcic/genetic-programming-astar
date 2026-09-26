import operator
import math
import random

from deap import base, creator, tools, gp

from grid import Grid
from astar import run_a_star, heuristic_dijkstra


 
# PROTECTED DIVISION
 

def protected_div(left, right):
    if abs(right) < 1e-6:
        return 1.0

    return left / right


 
# FITNESS AND INDIVIDUAL
 

if not hasattr(creator, "FitnessMax"):
    creator.create(
        "FitnessMax",
        base.Fitness,
        weights=(1.0,)
    )

if not hasattr(creator, "Individual"):
    creator.create(
        "Individual",
        gp.PrimitiveTree,
        fitness=creator.FitnessMax
    )


 
# PRIMITIVE SET
 

pset = gp.PrimitiveSet("MAIN", 5)

pset.addPrimitive(operator.add, 2)
pset.addPrimitive(operator.sub, 2)
pset.addPrimitive(operator.mul, 2)
pset.addPrimitive(protected_div, 2)

pset.addPrimitive(min, 2)
pset.addPrimitive(max, 2)

pset.renameArguments(ARG0="dx")
pset.renameArguments(ARG1="dy")
pset.renameArguments(ARG2="d_manhattan")
pset.renameArguments(ARG3="d_euclidean")
pset.renameArguments(ARG4="obs_density")


 
# TOOLBOX
 

toolbox = base.Toolbox()

toolbox.register(
    "expr",
    gp.genHalfAndHalf,
    pset=pset,
    min_=1,
    max_=2
)

toolbox.register(
    "individual",
    tools.initIterate,
    creator.Individual,
    toolbox.expr
)

toolbox.register(
    "population",
    tools.initRepeat,
    list,
    toolbox.individual
)

toolbox.register(
    "compile",
    gp.compile,
    pset=pset
)


 
# GRID
 

grid = Grid()


 
# START AND GOAL
 

start = grid.start
goal = grid.goal


 
# OPTIMAL PATH
 

optimal_path = run_a_star(
    grid,
    start,
    goal,
    heuristic_dijkstra
)

optimal_length = len(optimal_path)


 
# HEURISTIC
 

def calculate_heuristic(
    heuristic,
    current,
    goal,
    grid
):
    dx = goal[0] - current[0]
    dy = goal[1] - current[1]

    d_manhattan = (
        abs(dx) +
        abs(dy)
    )

    d_euclidean = math.sqrt(
        dx * dx +
        dy * dy
    )

    obs_density = 0.0

    return heuristic(
        dx,
        dy,
        d_manhattan,
        d_euclidean,
        obs_density
    )


 
# EVALUATION
 

def evaluate(individual):

    heuristic = toolbox.compile(
        expr=individual
    )

    def gp_heuristic(current, goal, grid):

        return calculate_heuristic(
            heuristic,
            current,
            goal,
            grid
        )

    path, visited = run_a_star(
        grid,
        start,
        goal,
        gp_heuristic
    )

     
    # NO PATH
     

    if not path:
        return (-1000.0,)

     
    # PATH LENGTH
     

    path_length = len(path)

    length_difference = abs(
        path_length - optimal_length
    )

     
    # VISITED NODES
     

    visited_count = len(visited)

     
    # TREE COMPLEXITY
     

    tree_depth = individual.height

     
    # FITNESS
     

    fitness = (
        -length_difference
        -0.01 * visited_count
        -0.01 * tree_depth
    )

    return (fitness,)


toolbox.register(
    "evaluate",
    evaluate
)


 
# SELECTION
 

toolbox.register(
    "select",
    tools.selTournament,
    tournsize=3
)


 
# CROSSOVER
 

toolbox.register(
    "mate",
    gp.cxOnePoint
)


 
# MUTATION
 

toolbox.register(
    "mutate",
    gp.mutUniform,
    expr=toolbox.expr,
    pset=pset
)


 
# POPULATION
 

population = toolbox.population(
    n=20
)


 
# INITIAL EVALUATION
 

for individual in population:

    individual.fitness.values = (
        toolbox.evaluate(individual)
    )


 
# EVOLUTION
 

number_of_generations = 20

for generation in range(
    number_of_generations
):

     
    # SELECTION
     

    selected = toolbox.select(
        population,
        len(population)
    )

     
    # CLONE
     

    offspring = list(
        map(
            toolbox.clone,
            selected
        )
    )

     
    # CROSSOVER
     

    for child1, child2 in zip(
        offspring[::2],
        offspring[1::2]
    ):

        if len(child1) > 1 and len(child2) > 1:

            toolbox.mate(
                child1,
                child2
            )

            del child1.fitness.values
            del child2.fitness.values

     
    # MUTATION
     

    for mutant in offspring:

        toolbox.mutate(
            mutant
        )

        del mutant.fitness.values

     
    # EVALUATION
     

    for individual in offspring:

        if not individual.fitness.valid:

            individual.fitness.values = (
                toolbox.evaluate(individual)
            )

     
    # NEW GENERATION
     

    population = offspring

     
    # BEST
     

    best_individual = tools.selBest(
        population,
        1
    )[0]

    print(
        "Generation:",
        generation,
        "| Best:",
        best_individual,
        "| Fitness:",
        best_individual.fitness.values[0]
    )


 
# FINAL RESULT
 

best_individual = tools.selBest(
    population,
    1
)[0]

print()
print("Best individual:")
print(best_individual)

print(
    "Fitness:",
    best_individual.fitness.values[0]
)

print(
    "Tree depth:",
    best_individual.height
)