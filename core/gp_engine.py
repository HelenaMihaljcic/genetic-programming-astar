import operator
from deap import base, creator, tools, gp


creator.create(
    "FitnessMax",
    base.Fitness,
    weights=(1.0,)
)

creator.create(
    "Individual",
    gp.PrimitiveTree,
    fitness=creator.FitnessMax
)


pset = gp.PrimitiveSet("MAIN", 2)

pset.addPrimitive(operator.add, 2)
pset.addPrimitive(operator.sub, 2)
pset.addPrimitive(operator.mul, 2)

pset.renameArguments(ARG0="x")
pset.renameArguments(ARG1="y")


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

population = toolbox.population(n=10)

for individual in population:
    print(individual)