def optimize_meals():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("MealOptimization")

    # Decision variables: number of turkey dinners and tuna sandwiches
    x_T = m.addVar(name="TurkeyDinner", lb=0, vtype=GRB.INTEGER)
    x_S = m.addVar(name="TunaSandwich", lb=0, vtype=GRB.INTEGER)

    # Set the objective: minimize total fat intake
    m.setObjective(12 * x_T + 8 * x_S, GRB.MINIMIZE)

    # Add constraints
    # Protein constraint
    m.addConstr(20 * x_T + 18 * x_S >= 150, name="ProteinRequirement")
    # Carbohydrate constraint
    m.addConstr(30 * x_T + 25 * x_S >= 200, name="CarbRequirement")
    # Proportion constraint: 3x_T - 2x_S <= 0
    m.addConstr(3 * x_T - 2 * x_S <= 0, name="TurkeyProportion")

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the optimal total fat intake
        return m.objVal
    else:
        # No feasible solution
        return None

# Example usage
print(optimize_meals())