def optimize_flooring_production(
    demand_hardwood=20000,
    demand_vinyl=10000,
    total_shipment=60000,
    max_hardwood=50000,
    max_vinyl=30000,
    profit_hardwood=2.5,
    profit_vinyl=3
):
    import gurobipy as gp
    from gurobipy import GRB

    # Create a new model
    model = gp.Model("Flooring_Production_Optimization")

    # Decision variables
    x = model.addVar(name="Hardwood", lb=0, ub=max_hardwood)
    y = model.addVar(name="Vinyl", lb=0, ub=max_vinyl)

    # Set the objective
    model.setObjective(profit_hardwood * x + profit_vinyl * y, GRB.MAXIMIZE)

    # Add constraints
    model.addConstr(x >= demand_hardwood, "HardwoodDemand")
    model.addConstr(y >= demand_vinyl, "VinylDemand")
    model.addConstr(x + y >= total_shipment, "TotalShipment")
    # The upper bounds are already enforced by variable bounds, but can be explicitly added
    # for clarity:
    model.addConstr(x <= max_hardwood, "HardwoodCap")
    model.addConstr(y <= max_vinyl, "VinylCap")

    # Optimize the model
    model.optimize()

    # Check if a feasible solution was found
    if model.status == GRB.OPTIMAL:
        # Return the optimal profit
        return model.objVal
    else:
        # No feasible solution
        return None
# Example usage
if __name__ == "__main__":
    max_profit = optimize_flooring_production()
    if max_profit is not None:
        print(f"Maximum Profit: {max_profit}")
    else:
        print("No feasible solution found.")