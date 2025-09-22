def optimize_vehicles():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("airport_vehicles")

    # Decision variables: number of 4-wheelers and 3-wheelers
    x = m.addVar(vtype=GRB.INTEGER, name="x")  # 4-wheeler
    y = m.addVar(vtype=GRB.INTEGER, name="y")  # 3-wheeler

    # Set the objective: minimize total number of vehicles
    m.setObjective(x + y, GRB.MINIMIZE)

    # Add constraints
    # Luggage capacity constraint
    m.addConstr(60 * x + 40 * y >= 1000, "luggage_constraint")
    # Pollution constraint
    m.addConstr(30 * x + 15 * y <= 430, "pollution_constraint")
    # Non-negativity is implicit in variable definition

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        return m.objVal
    else:
        return None
# Example usage
if __name__ == "__main__":
    min_vehicles = optimize_vehicles()
    if min_vehicles is not None:
        print(f"Minimum Total Number of Vehicles: {min_vehicles}")
    else:
        print("No feasible solution found.")