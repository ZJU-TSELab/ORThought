def optimize_vaccination(max_time=10000, min_pills=30):
    import gurobipy as gp
    from gurobipy import GRB

    # Create a new model
    model = gp.Model("Vaccination_Optimization")

    # Decision variables: number of pills and shots
    x = model.addVar(name="pill", vtype=GRB.INTEGER, lb=0)
    y = model.addVar(name="shot", vtype=GRB.INTEGER, lb=0)

    # Set the objective: maximize total vaccinated
    model.setObjective(x + y, GRB.MAXIMIZE)

    # Add constraints
    # Time constraint
    model.addConstr(10 * x + 20 * y <= max_time, name="time_limit")
    # Ratio constraint
    model.addConstr(y >= 3 * x, name="ratio")
    # Minimum pills
    model.addConstr(x >= min_pills, name="min_pills")

    # Optimize the model
    model.optimize()

    # Check if a feasible solution was found
    if model.status == GRB.OPTIMAL:
        # Return the maximum number of patients vaccinated
        return model.objVal
    else:
        # No feasible solution
        return None
# Example usage 
if __name__ == "__main__":
    max_vaccinated = optimize_vaccination()
    if max_vaccinated is not None:
        print(f"Maximum Patients Vaccinated: {max_vaccinated}")
    else:
        print("No feasible solution found.")