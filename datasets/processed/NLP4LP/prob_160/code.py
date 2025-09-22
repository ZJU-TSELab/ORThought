def optimize_mail_delivery():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("MailDeliveryOptimization")
    
    # Decision variables
    R = m.addVar(vtype=GRB.INTEGER, name="RegularTrips", lb=0, ub=20)
    S = m.addVar(vtype=GRB.INTEGER, name="SpeedTrips", lb=0)
    
    # Set objective: minimize total gas consumption
    m.setObjective(10 * R + 20 * S, GRB.MINIMIZE)
    
    # Add constraints
    # Mail delivery constraint
    m.addConstr(20 * R + 30 * S >= 1000, name="MailDelivery")
    # Regular trips limit
    m.addConstr(R <= 20, name="MaxRegularTrips")
    # Speed trips at least 50% of total trips
    m.addConstr(S >= R, name="SpeedAtLeastHalf")
    
    # Optimize the model
    m.optimize()
    
    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the optimal total gas consumption
        return m.objVal
    else:
        # No feasible solution
        return None
# Example usage
if __name__ == "__main__":
    min_gas = optimize_mail_delivery()
    if min_gas is not None:
        print(f"Minimum Total Gas Consumption: {min_gas}")
    else:
        print("No feasible solution found.")