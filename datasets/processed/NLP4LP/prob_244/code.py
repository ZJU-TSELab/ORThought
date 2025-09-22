def optimize_car_jacks():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("CarJacksOptimization")
    
    # Decision variables
    # x: number of automatic electric jacks
    # y: number of gas-powered jacks
    x = m.addVar(vtype=GRB.INTEGER, name="electric_jacks")
    y = m.addVar(vtype=GRB.INTEGER, name="gas_jacks")
    
    # Set the objective: maximize total cars processed
    m.setObjective(5 * x + 4 * y, GRB.MAXIMIZE)
    
    # Add constraints
    m.addConstr(x <= 14, "max_electric_jacks")
    m.addConstr(6 * x <= 50, "electricity_limit")
    m.addConstr(7 * y <= 80, "gas_limit")
    m.addConstr(x >= 0, "non_neg_electric")
    m.addConstr(y >= 0, "non_neg_gas")
    
    # Optimize the model
    m.optimize()
    
    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the maximum number of cars processed
        return m.objVal
    else:
        # No feasible solution
        return None
# Example usage
if __name__ == "__main__":
    max_cars = optimize_car_jacks()
    if max_cars is not None:
        print(f"Maximum Cars Processed: {max_cars}")
    else:
        print("No feasible solution found.")