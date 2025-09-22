def optimize_production(profit_A=30,
                        profit_B=10,
                        hours_per_A=6,
                        hours_per_B=3,
                        max_hours=40,
                        min_B_ratio=3,
                        max_A_storage=4):
    import gurobipy as gp
    from gurobipy import GRB

    # Create a new model
    model = gp.Model("Production_Optimization")

    # Decision variables: number of units of A and B
    x_A = model.addVar(vtype=GRB.INTEGER, name="x_A", lb=0)
    x_B = model.addVar(vtype=GRB.INTEGER, name="x_B", lb=0)

    # Set objective: maximize profit
    model.setObjective(profit_A * x_A + profit_B * x_B, GRB.MAXIMIZE)

    # Add constraints
    # Production time constraint
    model.addConstr(hours_per_A * x_A + hours_per_B * x_B <= max_hours,
                    "TimeLimit")
    # Market demand constraint for B
    model.addConstr(x_B >= min_B_ratio * x_A, "DemandB")
    # Storage space constraint for A
    model.addConstr(x_A <= max_A_storage, "StorageA")

    # Optimize the model
    model.optimize()

    # Check if a feasible solution was found
    if model.status == GRB.OPTIMAL:
        return model.objVal
    else:
        return None
if __name__ == "__main__":  # pragma: no cover
    result = optimize_production()
    if result is not None:
        print(f"Optimal profit: {result}")
    else:
        print("No feasible solution found.")