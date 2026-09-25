import operator
from deap import base, creator, tools, gp


 
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

pset.renameArguments(ARG0="x")
pset.renameArguments(ARG1="y")


 
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


 
# EVALUATION
 

def evaluate(individual):
    func = toolbox.compile(expr=individual)

    result = func(2, 3)

    error = abs(result - 10)

    return (-error,)


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
 

population = toolbox.population(n=10)


 
# INITIAL EVALUATION
 

for individual in population:
    individual.fitness.values = toolbox.evaluate(individual)


 
# EVOLUTION
 

number_of_generations = 10

for generation in range(number_of_generations):

     
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

        toolbox.mutate(mutant)

        del mutant.fitness.values

     
    # EVALUATE NEW INDIVIDUALS
     

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

print("\nBest individual:")
print(best_individual)

print(
    "Fitness:",
    best_individual.fitness.values[0]
)

func = toolbox.compile(
    expr=best_individual
)

print(
    "Result for x=2, y=3:",
    func(2, 3)
)