def optimize_senior_home_snacks():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("SeniorHomeSnacks")

    # Decision variables: cups of spinach and soybeans
    x = m.addVar(name="spinach", lb=0)
    y = m.addVar(name="soybeans", lb=0)

    # Set the objective: maximize total calories
    m.setObjective(30 * x + 100 * y, GRB.MAXIMIZE)

    # Add constraints
    # Fibre constraint
    m.addConstr(100 * x + 80 * y >= 12000, name="fibre")
    # Iron constraint
    m.addConstr(5 * x + 12 * y >= 300, name="iron")
    # Quantity relationship: spinach exceeds soybeans by at least 1 cup
    m.addConstr(x >= y + 1, name="quantity_relation")

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the maximum caloric intake
        return m.objVal
    else:
        # No feasible solution
        return None
# Example usage
if __name__ == "__main__":
    max_calories = optimize_senior_home_snacks()
    if max_calories is not None:
        print(f"Maximum Caloric Intake: {max_calories:.2f} calories")
    else:
        print("No feasible solution found.")