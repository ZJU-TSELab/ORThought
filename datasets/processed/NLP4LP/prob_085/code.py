def optimize_chocolate_production(cocoa_available=2000, milk_available=1750,
                                  time_milk=15, time_dark=12):
    import gurobipy as gp
    from gurobipy import GRB

    # Create a new model
    model = gp.Model("Chocolate_Production_MinTime")

    # Decision variables: number of milk and dark chocolate bars
    x = model.addVar(name="MilkBars", vtype=GRB.INTEGER, lb=0)
    y = model.addVar(name="DarkBars", vtype=GRB.INTEGER, lb=0)

    # Set objective: minimize total production time
    model.setObjective(time_milk * x + time_dark * y, GRB.MINIMIZE)

    # Add resource constraints
    model.addConstr(4 * x + 6 * y <= cocoa_available, "CocoaConstraint")
    model.addConstr(7 * x + 3 * y <= milk_available, "MilkConstraint")

    # Add production ratio constraint
    model.addConstr(x >= 2 * y, "MilkDarkRatio")

    # Optimize the model
    model.optimize()

    # Check if a feasible solution was found
    if model.status == GRB.OPTIMAL:
        # Return the minimized total time
        return model.objVal
    else:
        # No feasible solution
        return None
# Example usage
if __name__ == "__main__":
    min_time = optimize_chocolate_production()
    if min_time is not None:
        print(f"Minimum Total Production Time: {min_time}")
    else:
        print("No feasible solution found.")