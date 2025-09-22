def optimize_lawn_mowing(small_team_min=10, large_team_min=6, total_employees=150):
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("LawnMowingOptimization")
    m.setParam('OutputFlag', 0)  # Suppress Gurobi output

    # Decision variables
    s = m.addVar(vtype=GRB.INTEGER, name="small_teams")
    l = m.addVar(vtype=GRB.INTEGER, name="large_teams")

    # Set objective: maximize total lawn area
    m.setObjective(50 * s + 80 * l, GRB.MAXIMIZE)

    # Add constraints
    # Employee constraint
    m.addConstr(3 * s + 5 * l <= total_employees, name="employee_limit")
    # Ratio constraint
    m.addConstr(s >= 3 * l, name="ratio_constraint")
    # Minimum number of small teams
    m.addConstr(s >= small_team_min, name="min_small_teams")
    # Minimum number of large teams
    m.addConstr(l >= large_team_min, name="min_large_teams")

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the maximum lawn area
        return m.objVal
    else:
        # No feasible solution
        return None
# Example usage
if __name__ == "__main__":
    max_lawn_area = optimize_lawn_mowing()
    if max_lawn_area is not None:
        print(f"Maximum Lawn Area: {max_lawn_area}")
    else:
        print("No feasible solution found.")