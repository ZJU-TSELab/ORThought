def optimize_grills():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("Grill_Optimization")

    # Decision variables: number of gas and electric grills
    G = m.addVar(vtype=GRB.INTEGER, name="GasGrills", lb=0)
    E = m.addVar(vtype=GRB.INTEGER, name="ElectricGrills", lb=0)

    # Set the objective: minimize total number of grills
    m.setObjective(G + E, GRB.MINIMIZE)

    # Add constraints
    # Cooking capacity constraint
    m.addConstr(20 * G + 30 * E >= 150, name="CookingCapacity")
    # Oil usage constraint
    m.addConstr(20 * G + 25 * E <= 140, name="OilUsage")
    # Taste preference constraint
    m.addConstr(E <= G - 1, name="TastePreference")

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the optimal total number of grills
        return m.objVal
    else:
        # No feasible solution
        return None
# Example usage
if __name__ == "__main__":
    min_grills = optimize_grills()
    if min_grills is not None:
        print(f"Minimum Total Number of Grills: {min_grills}")
    else:
        print("No feasible solution found.")