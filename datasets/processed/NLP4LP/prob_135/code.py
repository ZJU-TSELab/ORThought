def optimize_fruit_packs():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("Fruit_Packs_Minimize_Sugar")

    # Decision variables: number of blueberry and strawberry packs
    x = m.addVar(vtype=GRB.INTEGER, name="Blueberry_Packs", lb=0)
    y = m.addVar(vtype=GRB.INTEGER, name="Strawberry_Packs", lb=0)

    # Set objective: minimize total sugar intake
    m.setObjective(5 * x + 7 * y, GRB.MINIMIZE)

    # Add constraints
    m.addConstr(3 * x + y >= 90, "AntiOxidant_Requirement")
    m.addConstr(5 * x + 7 * y >= 100, "Mineral_Requirement")
    m.addConstr(y >= 3 * x, "Strawberry_to_Blueberry_Ratio")

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the minimum sugar intake
        return m.objVal
    else:
        # No feasible solution
        return None
# Example usage
if __name__ == "__main__":
    min_sugar = optimize_fruit_packs()
    if min_sugar is not None:
        print(f"Minimum Sugar Intake: {min_sugar}")
    else:
        print("No feasible solution found.")