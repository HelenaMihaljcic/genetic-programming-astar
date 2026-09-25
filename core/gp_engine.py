import operator

from deap import base, creator, tools, gp

from grid import Grid
from a_star import run_a_star, heuristic_dijkstra


 
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
 

pset = gp.PrimitiveSet("MAIN", 2)

pset.addPrimitive(operator.add, 2)
pset.addPrimitive(operator.sub, 2)
pset.addPrimitive(operator.mul, 2)

pset.renameArguments(ARG0="dx")
pset.renameArguments(ARG1="dy")


 
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


 
# COMPILE
 

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


 
# EVALUATION
 

def evaluate(individual):

    heuristic = toolbox.compile(
        expr=individual
    )

    path, visited = run_a_star(
        grid,
        start,
        goal,
        heuristic
    )

    if not path:
        return (-1000.0,)

    path_length = len(path)

    length_difference = abs(
        path_length - optimal_length
    )

    fitness = -length_difference

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


 
# CREATE POPULATION
 

population = toolbox.population(
    n=10
)


 
# INITIAL EVALUATION
 

for individual in population:

    individual.fitness.values = (
        toolbox.evaluate(individual)
    )


 
# EVOLUTION
 

number_of_generations = 10

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

     
    # BEST INDIVIDUAL
     

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

print(
    "\nBest individual:"
)

print(
    best_individual
)

print(
    "Fitness:",
    best_individual.fitness.values[0]
)