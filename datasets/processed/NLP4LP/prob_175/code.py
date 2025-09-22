def minimize_animals(
    bricks_required=1000,
    bricks_per_cow=20,
    bricks_per_elephant=50
):
    import gurobipy as gp
    from gurobipy import GRB

    # Create a new model
    model = gp.Model("Minimize Animals")

    # Decision variables: number of cows and elephants
    x = model.addVar(vtype=GRB.INTEGER, name="cows", lb=0)
    y = model.addVar(vtype=GRB.INTEGER, name="elephants", lb=0)

    # Set the objective: minimize total animals
    model.setObjective(x + y, GRB.MINIMIZE)

    # Add constraints
    # Brick transportation constraint
    model.addConstr(bricks_per_cow * x + bricks_per_elephant * y >= bricks_required, "bricks_constraint")
    # Elephants cannot exceed cows
    model.addConstr(y <= x, "elephants_not_exceed_cows")
    # At most twice the number of cows as elephants
    model.addConstr(x <= 2 * y, "cows_at_most_twice_elephants")

    # Optimize the model
    model.optimize()

    # Check if a feasible solution was found
    if model.status == GRB.OPTIMAL:
        total_animals = x.X + y.X
        return total_animals
    else:
        return None
# Example usage
if __name__ == "__main__":
    total_animals = minimize_animals()
    if total_animals is not None:
        print(f"Minimum total number of animals: {total_animals}")
    else:
        print("No feasible solution found.")