def optimize_crepe_production():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("Crepe_Production")

    # Decision variables: number of chocolate and peanut butter crepes
    C = m.addVar(name="Chocolate_Crepes", vtype=GRB.INTEGER, lb=0)
    P = m.addVar(name="Peanut_Butter_Crepes", vtype=GRB.INTEGER, lb=0)

    # Set objective: minimize total crepe mix
    m.setObjective(6 * C + 7 * P, GRB.MINIMIZE)

    # Add constraints
    m.addConstr(3 * C <= 400, name="Chocolate_Spread_Limit")
    m.addConstr(4 * P <= 450, name="Peanut_Butter_Spread_Limit")
    m.addConstr(P >= C + 1, name="Popularity_Preference")
    m.addConstr(P <= 3 * C, name="Percentage_Constraint")

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the optimal total crepe mix used
        return m.objVal
    else:
        # No feasible solution found
        return None
# Example usage
if __name__ == "__main__":
    min_crepe_mix = optimize_crepe_production()
    if min_crepe_mix is not None:
        print(f"Minimum Total Crepe Mix Used: {min_crepe_mix}")
    else:
        print("No feasible solution found.")