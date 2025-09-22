def optimize_appliances():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("Appliance_Optimization")

    # Decision variables: number of refrigerators and stoves
    # Both are integers and non-negative
    x = m.addVar(vtype=GRB.INTEGER, name="Refrigerators", lb=0)
    y = m.addVar(vtype=GRB.INTEGER, name="Stoves", lb=0)

    # Set the objective: maximize profit
    m.setObjective(400 * x + 260 * y, GRB.MAXIMIZE)

    # Add constraints
    m.addConstr(60 * x + 45 * y <= 20000, "MoverTime")
    m.addConstr(20 * x + 25 * y <= 13000, "SetupTime")

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the optimal profit
        return m.objVal
    else:
        # No feasible solution found
        return None
# Example usage
if __name__ == "__main__":
    max_profit = optimize_appliances()
    if max_profit is not None:
        print(f"Maximum Profit: ${max_profit}")
    else:
        print("No feasible solution found.")