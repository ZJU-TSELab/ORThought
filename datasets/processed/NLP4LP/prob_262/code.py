def optimize_transportation():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("desert_transportation")

    # Decision variables: number of trips
    x = m.addVar(vtype=GRB.INTEGER, name="camel_trips", lb=0)
    y = m.addVar(vtype=GRB.INTEGER, name="truck_trips", lb=0)
    max_hour = m.addVar(vtype=GRB.INTEGER, name="max_hours", lb=0)

    # Set objective: minimize total hours
    m.setObjective(max_hour, GRB.MINIMIZE)
    # m.setObjective(12 * x + 5 * y, GRB.MINIMIZE)

    # Add constraints
    # Delivery constraint
    m.addConstr(50 * x + 150 * y >= 1500, name="delivery_requirement")
    # Preference constraint
    m.addConstr(x >= y + 1, name="more_camel_trips")
    # Maximum hours constraint
    m.addConstr(12 * x <= max_hour, name="max_hours_camel")
    m.addConstr(5 * y <= max_hour, name="max_hours_truck")
    
    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the optimal total hours
        return m.objVal
    else:
        # No feasible solution
        return None

# Example usage
print(optimize_transportation())