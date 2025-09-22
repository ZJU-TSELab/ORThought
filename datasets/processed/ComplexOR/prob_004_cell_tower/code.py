def optimize_cell_tower_coverage(delta=None, cost=None, population=None, budget=None):
    from gurobipy import Model, GRB

    # Default data based on the provided sample
    if delta is None:
        delta = [[1, 0, 1], [0, 1, 0]]
    if cost is None:
        cost = [3, 4]
    if population is None:
        population = [100, 200, 150]
    if budget is None:
        budget = 4

    m = len(cost)       # Number of potential sites
    n = len(population) # Number of regions

    # Create model
    model = Model("CellTowerCoverage")

    # Decision variables
    y = model.addVars(m, vtype=GRB.BINARY, name="y")
    x = model.addVars(n, vtype=GRB.BINARY, name="x")

    # Objective: maximize total covered population
    model.setObjective(
        sum(population[j] * x[j] for j in range(n)),
        GRB.MAXIMIZE
    )

    # Coverage constraints
    for j in range(n):
        # sum over sites that cover region j
        covering_sites = [i for i in range(m) if delta[i][j] == 1]
        model.addConstr(
            x[j] <= sum(y[i] for i in covering_sites),
            name=f"coverage_{j}"
        )

    # Budget constraint
    model.addConstr(
        sum(cost[i] * y[i] for i in range(m)) <= budget,
        name="budget"
    )

    # Optimize the model
    model.optimize()

    # Check if a feasible solution was found
    if model.status == GRB.OPTIMAL:
        # Return the maximum total covered population
        return model.objVal
    else:
        # No feasible solution found
        return None
if __name__ == "__main__":
    result = optimize_cell_tower_coverage()
    print(f"Maximum total covered population: {result}")