def optimize_property_selection(income_property1=12500,
                                income_property2=35000,
                                income_property3=23000,
                                income_property4=100000,
                                cost_property1=1.5,
                                cost_property2=2.1,
                                cost_property3=2.3,
                                cost_property4=4.2,
                                budget=7):
    import gurobipy as gp
    from gurobipy import GRB

    # Create a new model
    model = gp.Model("Property_Selection_MaxIncome")

    # Decision variables: binary for each property
    y1 = model.addVar(vtype=GRB.BINARY, name="Property1")
    y2 = model.addVar(vtype=GRB.BINARY, name="Property2")
    y3 = model.addVar(vtype=GRB.BINARY, name="Property3")
    y4 = model.addVar(vtype=GRB.BINARY, name="Property4")

    # Set objective: maximize total income
    model.setObjective(
        income_property1 * y1 + income_property2 * y2 + income_property3 * y3 +
        income_property4 * y4, GRB.MAXIMIZE)

    # Add budget constraint
    model.addConstr(cost_property1 * y1 + cost_property2 * y2 +
                    cost_property3 * y3 + cost_property4 * y4 <= budget,
                    name="BudgetConstraint")

    # Add property exclusivity constraint
    model.addConstr(y4 + y3 <= 1, name="Property3_Property4_Exclusion")

    # Optimize the model
    model.optimize()

    # Check if a feasible solution was found
    if model.status == GRB.OPTIMAL:
        # Return the maximum total income
        return model.objVal
    else:
        # No feasible solution found
        return None
if __name__ == "__main__":
    result = optimize_property_selection()
    if result is not None:
        print(f"Optimal total income: {result}")
    else:
        print("No feasible solution found.")