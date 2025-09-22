def optimize_keyboard_production(
    price_full=2800,
    price_semi=2400,
    chips_available=3500,
    hours_available=6,
    production_time=1.2
):
    import gurobipy as gp
    from gurobipy import GRB

    # Create a new model
    model = gp.Model("Keyboard_Production_Maximize_Revenue")

    # Decision variables: number of full-weighted and semi-weighted keyboards
    x = model.addVar(vtype=GRB.INTEGER, name="Full_Weighted_Keyboard")
    y = model.addVar(vtype=GRB.INTEGER, name="Semi_Weighted_Keyboard")

    # Set objective: maximize total revenue
    model.setObjective(price_full * x + price_semi * y, GRB.MAXIMIZE)

    # Add chip constraint
    model.addConstr(20 * x + 15 * y <= chips_available, "Chip_Limit")

    # Add production time constraint
    # Since each takes 1.2 hours, total hours for x and y
    model.addConstr(production_time * (x + y) <= hours_available, "Time_Limit")

    # Set non-negativity (implicit with variable type=GRB.INTEGER and default bounds)
    # Solve the model
    model.optimize()

    # Check if a feasible solution was found
    if model.status == GRB.OPTIMAL:
        # Return the optimal total revenue
        return model.objVal
    else:
        # No feasible solution found
        return None
# Example usage
if __name__ == "__main__":
    max_revenue = optimize_keyboard_production()
    if max_revenue is not None:
        print(f"Maximum Revenue: ${max_revenue}")
    else:
        print("No feasible solution found.")