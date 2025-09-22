def optimize_workbooks():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("Workbook_Production")

    # Decision variables: number of math and English workbooks
    # They are integers because you can't produce fractional workbooks
    x = m.addVar(lb=40, ub=140, vtype=GRB.INTEGER, name="Math_Workbooks")
    y = m.addVar(lb=60, ub=170, vtype=GRB.INTEGER, name="English_Workbooks")

    # Set the objective: maximize profit
    m.setObjective(15 * x + 17 * y, GRB.MAXIMIZE)

    # Add demand constraint
    m.addConstr(x + y >= 200, "Demand_Constraint")

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the maximum profit
        return m.objVal
    else:
        # No feasible solution found
        return None
# Example usage
if __name__ == "__main__":
    max_profit = optimize_workbooks()
    if max_profit is not None:
        print(f"Maximum Profit: ${max_profit}")
    else:
        print("No feasible solution found.")