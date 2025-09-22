def optimize_tea_harvest(
    total_acres=500,
    total_fuel=9000,
    max_waste=6000
):
    import gurobipy as gp
    from gurobipy import GRB

    # Create a new model
    model = gp.Model("Tea_Harvest_Maximization")

    # Decision variables: acres assigned to traditional and modern machines
    x = model.addVar(name="Traditional_Acres", lb=0)
    y = model.addVar(name="Modern_Acres", lb=0)

    # Set the objective: maximize total tea leaves
    model.setObjective(30 * x + 40 * y, GRB.MAXIMIZE)

    # Add constraints
    # Land constraint
    model.addConstr(x + y <= total_acres, name="Land_Limit")
    # Fuel constraint
    model.addConstr(20 * x + 15 * y <= total_fuel, name="Fuel_Limit")
    # Waste constraint
    model.addConstr(10 * x + 15 * y <= max_waste, name="Waste_Limit")

    # Optimize the model
    model.optimize()

    # Check if a feasible solution was found
    if model.status == GRB.OPTIMAL:
        # Return the maximum total tea leaves picked
        return model.objVal
    else:
        # No feasible solution found
        return None
# Example usage
if __name__ == "__main__":
    max_tea_leaves = optimize_tea_harvest()
    if max_tea_leaves is not None:
        print(f"Maximum Total Tea Leaves Picked: {max_tea_leaves}")
    else:
        print("No feasible solution found.")