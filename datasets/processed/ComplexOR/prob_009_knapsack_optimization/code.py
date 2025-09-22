def solve_knapsack(item_values=None, item_weights=None, max_weight_knapsack=None):
    from gurobipy import Model, GRB

    # Default data based on the provided problem
    if item_values is None:
        item_values = [60, 100, 120]
    if item_weights is None:
        item_weights = [10, 20, 30]
    if max_weight_knapsack is None:
        max_weight_knapsack = 50

    n_items = len(item_values)

    # Create a new model
    model = Model("Knapsack")

    # Add decision variables: x_i in {0,1}
    x = model.addVars(n_items, vtype=GRB.BINARY, name="x")

    # Set the objective: maximize total value
    model.setObjective(
        sum(item_values[i] * x[i] for i in range(n_items)),
        GRB.MAXIMIZE
    )

    # Add weight constraint
    model.addConstr(
        sum(item_weights[i] * x[i] for i in range(n_items)) <= max_weight_knapsack,
        name="WeightConstraint"
    )

    # Optimize the model
    model.optimize()

    # Check if a feasible solution was found
    if model.status == GRB.OPTIMAL:
        return model.objVal
    else:
        return None
if __name__ == "__main__":
    result = solve_knapsack()
    if result is not None:
        print(f"Maximum value in knapsack: {result}")
    else:
        print("No feasible solution found.")