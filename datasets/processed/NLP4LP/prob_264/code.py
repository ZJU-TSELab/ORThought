from gurobipy import Model, GRB


def minimize_chemical_time():
    # Create a new model
    model = Model("chemical_time_optimization")

    # Variables
    x = model.addVar(name="x", lb=300)
    y = model.addVar(name="y", lb=0)

    # Objective function: minimize 30x + 45y
    model.setObjective(30 * x + 45 * y, GRB.MINIMIZE)

    # Constraints
    model.addConstr(x <= (1 / 3) * y, "A_B_ratio")
    model.addConstr(x + y >= 1500, "total_chemicals")

    # Optimize
    model.optimize()

    # Check if solution exists
    if model.status == GRB.OPTIMAL:
        return model.objVal
    else:
        return None


# Example usage
if __name__ == "__main__":
    result = minimize_chemical_time()
    print(f"Minimum total time for bread to be ready: {result}")
