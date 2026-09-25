import operator
from deap import base, creator, tools, gp


# =========================
# FITNESS AND INDIVIDUAL
# =========================

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


# =========================
# PRIMITIVE SET
# =========================

pset = gp.PrimitiveSet("MAIN", 2)

pset.addPrimitive(operator.add, 2)
pset.addPrimitive(operator.sub, 2)
pset.addPrimitive(operator.mul, 2)

pset.renameArguments(ARG0="x")
pset.renameArguments(ARG1="y")


# =========================
# TOOLBOX
# =========================

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


# =========================
# COMPILE
# =========================

toolbox.register(
    "compile",
    gp.compile,
    pset=pset
)


# =========================
# EVALUATION
# =========================

def evaluate(individual):
    func = toolbox.compile(expr=individual)

    result = func(2, 3)

    error = abs(result - 10)

    return (-error,)


toolbox.register(
    "evaluate",
    evaluate
)


# =========================
# SELECTION
# =========================

toolbox.register(
    "select",
    tools.selTournament,
    tournsize=3
)


# =========================
# CROSSOVER
# =========================

toolbox.register(
    "mate",
    gp.cxOnePoint
)


# =========================
# MUTATION
# =========================

toolbox.register(
    "mutate",
    gp.mutUniform,
    expr=toolbox.expr,
    pset=pset
)


# =========================
# CREATE POPULATION
# =========================

population = toolbox.population(n=10)


# =========================
# EVALUATE POPULATION
# =========================

for individual in population:
    individual.fitness.values = toolbox.evaluate(individual)


# =========================
# SELECT INDIVIDUALS
# =========================

selected = toolbox.select(
    population,
    len(population)
)


# =========================
# CLONE SELECTED INDIVIDUALS
# =========================

offspring = list(
    map(
        toolbox.clone,
        selected
    )
)


# =========================
# APPLY CROSSOVER
# =========================

for child1, child2 in zip(
    offspring[::2],
    offspring[1::2]
):
    if len(child1) > 1 and len(child2) > 1:
        toolbox.mate(child1, child2)

        del child1.fitness.values
        del child2.fitness.values


# =========================
# APPLY MUTATION
# =========================

for mutant in offspring:
    toolbox.mutate(mutant)

    del mutant.fitness.values


# =========================
# PRINT RESULTS
# =========================

print("Original population:")

for individual in population:
    print(
        individual,
        "fitness:",
        individual.fitness.values[0]
    )


print("\nSelected population:")

for individual in selected:
    print(
        individual,
        "fitness:",
        individual.fitness.values[0]
    )


print("\nOffspring after crossover and mutation:")

for individual in offspring:
    print(
        individual,
        "fitness: invalid"
    )