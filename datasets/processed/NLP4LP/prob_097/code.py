def optimize_batches(
    min_regular_batches=10,
    max_resource_medicinal=3000,
    max_resource_rehydration=3500
):
    import gurobipy as gp
    from gurobipy import GRB

    # Create a new model
    model = gp.Model("Batch_Production_Optimization")

    # Decision variables
    # x: number of regular batches
    # y: number of premium batches
    x = model.addVar(name="x", vtype=GRB.INTEGER, lb=min_regular_batches)
    y = model.addVar(name="y", vtype=GRB.INTEGER, lb=0)

    # Set objective: maximize total number of treated people
    model.setObjective(50 * x + 30 * y, GRB.MAXIMIZE)

    # Add resource constraints
    model.addConstr(50 * x + 40 * y <= max_resource_medicinal, "Medicinal")
    model.addConstr(40 * x + 60 * y <= max_resource_rehydration, "Rehydration")

    # Add batch relationship constraint: x < y
    # Since variables are integers, x <= y - 1
    model.addConstr(x <= y - 1, "BatchRelation")

    # Optional: To ensure logical bounds, but already set lb for x
    # model.addConstr(x >= 10, "MinRegularBatches") # Already set lb=10

    # Optimize the model
    model.optimize()

    # Check if a feasible solution was found
    if model.status == GRB.OPTIMAL:
        # Return the maximum total treated people
        return model.objVal
    else:
        # No feasible solution
        return None
# Example usage
if __name__ == "__main__":
    max_treated_people = optimize_batches()
    if max_treated_people is not None:
        print(f"Maximum Total Number of Treated People: {max_treated_people}")
    else:
        print("No feasible solution found.")