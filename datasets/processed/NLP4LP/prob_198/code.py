def optimize_dog_food(
    cost_regular=20,
    cost_premium=35,
    calcium_regular=4,
    calcium_premium=12,
    vitamin_regular=7,
    vitamin_premium=10,
    protein_regular=10,
    protein_premium=16,
    calcium_req=15,
    vitamin_req=20,
    protein_req=20
):
    import gurobipy as gp
    from gurobipy import GRB

    # Create a new model
    model = gp.Model("DogFoodOptimization")

    # Decision variables: number of bags of each type
    x = model.addVar(vtype=GRB.INTEGER, lb=0, name="Regular")
    y = model.addVar(vtype=GRB.INTEGER, lb=0, name="Premium")

    # Set objective: minimize total cost
    model.setObjective(
        cost_regular * x + cost_premium * y,
        GRB.MINIMIZE
    )

    # Add constraints
    # Calcium constraint
    model.addConstr(
        calcium_regular * x + calcium_premium * y >= calcium_req,
        name="Calcium"
    )
    # Vitamin constraint
    model.addConstr(
        vitamin_regular * x + vitamin_premium * y >= vitamin_req,
        name="Vitamin"
    )
    # Protein constraint
    model.addConstr(
        protein_regular * x + protein_premium * y >= protein_req,
        name="Protein"
    )

    # Optimize the model
    model.optimize()

    # Check if a feasible solution was found
    if model.status == GRB.OPTIMAL:
        # Return the optimal cost
        return model.objVal
    else:
        # No feasible solution
        return None
# Example usage
if __name__ == "__main__":
    min_cost = optimize_dog_food()
    if min_cost is not None:
        print(f"Minimum Cost: {min_cost}")
    else:
        print("No feasible solution found.")