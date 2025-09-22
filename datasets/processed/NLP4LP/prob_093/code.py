def optimize_vitamins():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("VitaminIntakeMaximization")

    # Decision variables: number of orange and apple juice boxes
    x = m.addVar(name="orange_boxes", vtype=GRB.INTEGER, lb=3)
    y = m.addVar(name="apple_boxes", vtype=GRB.INTEGER, lb=0)

    # Set the objective: maximize total vitamin D
    m.setObjective(10 * x + 12 * y, GRB.MAXIMIZE)

    # Add constraints
    # Vitamin C constraint
    m.addConstr(8 * x + 6 * y <= 300, name="VitaminC_limit")
    # Preference constraint: at least 3 times as many apple as orange
    m.addConstr(y >= 3 * x, name="Preference")
    # Minimum orange boxes
    m.addConstr(x >= 3, name="Min_orange")

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the maximum vitamin D intake
        return m.objVal
    else:
        # No feasible solution
        return None
# Example usage
if __name__ == "__main__":
    max_vitamin_d = optimize_vitamins()
    if max_vitamin_d is not None:
        print(f"Maximum Vitamin D Intake: {max_vitamin_d}")
    else:
        print("No feasible solution found.")