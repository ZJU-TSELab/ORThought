def optimize_toy_production(labor_hours=1000,
                            inspection_hours=500,
                            demand_high=50,
                            demand_mid=80,
                            demand_low=150,
                            profit_high=300,
                            profit_mid=200,
                            profit_low=100,
                            labor_high=17,
                            labor_mid=10,
                            labor_low=2,
                            inspect_high=8,
                            inspect_mid=4,
                            inspect_low=2):
    import gurobipy as gp
    from gurobipy import GRB

    # Create a new model
    model = gp.Model("Toy_Production_Maximize_Profit")

    # Decision variables: number of units to produce for each type
    x_H = model.addVar(vtype=GRB.INTEGER, name="HighEnd", lb=0, ub=demand_high)
    x_M = model.addVar(vtype=GRB.INTEGER, name="MidRange", lb=0, ub=demand_mid)
    x_L = model.addVar(vtype=GRB.INTEGER, name="LowEnd", lb=0, ub=demand_low)

    # Set objective: maximize total profit
    model.setObjective(profit_high * x_H + profit_mid * x_M + profit_low * x_L,
                       GRB.MAXIMIZE)

    # Add labor hours constraint
    model.addConstr(labor_high * x_H + labor_mid * x_M + labor_low * x_L
                    <= labor_hours,
                    name="LaborHours")

    # Add inspection hours constraint
    model.addConstr(inspect_high * x_H + inspect_mid * x_M + inspect_low * x_L
                    <= inspection_hours,
                    name="InspectionHours")

    # Optimize the model
    model.optimize()

    # Check if a feasible solution was found
    if model.status == GRB.OPTIMAL:
        # Return the maximum profit value
        return model.objVal
    else:
        # No feasible solution found
        return None
if __name__ == "__main__":
    result = optimize_toy_production()
    if result is not None:
        print(f"Optimal total profit: {result}")
    else:
        print("No feasible solution found.")