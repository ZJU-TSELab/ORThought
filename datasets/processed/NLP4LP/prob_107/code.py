def optimize_vitamin_batches():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("Vitamin_Batches")

    # Decision variables
    # x: batches of vitamin shots
    # y: batches of vitamin pills
    x = m.addVar(vtype=GRB.INTEGER, name="x", lb=0)
    y = m.addVar(vtype=GRB.INTEGER, name="y", lb=0)

    # Set the objective: maximize total people served
    m.setObjective(10 * x + 7 * y, GRB.MAXIMIZE)

    # Add constraints
    m.addConstr(30 * x + 50 * y <= 1200, "VitaminC")
    m.addConstr(40 * x + 30 * y <= 1500, "VitaminD")
    # Replace the strict inequality y > x with y >= x + 1
    m.addConstr(y >= x + 1, "BatchSizeRelation")
    m.addConstr(x <= 10, "MaxShots")

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the maximum number of people served
        return m.objVal
    else:
        # No feasible solution
        return None
# Example usage
if __name__ == "__main__":
    max_people_served = optimize_vitamin_batches()
    if max_people_served is not None:
        print(f"Maximum People Served: {max_people_served}")
    else:
        print("No feasible solution found.")