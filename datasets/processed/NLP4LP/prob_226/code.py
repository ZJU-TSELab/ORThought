def optimize_concerts():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("ConcertOptimization")

    # Decision variables: number of pop and R&B concerts
    x = m.addVar(vtype=GRB.INTEGER, name="PopConcerts", lb=0)
    y = m.addVar(vtype=GRB.INTEGER, name="R&BConcerts", lb=0)

    # Set the objective: minimize total number of concerts
    m.setObjective(x + y, GRB.MINIMIZE)

    # Audience constraint
    m.addConstr(100 * x + 240 * y >= 10000, "AudienceRequirement")

    # Practice days constraint
    m.addConstr(2 * x + 4 * y <= 180, "PracticeDaysLimit")

    # R&B performance limit: y <= (2/3) * x
    m.addConstr(y <= (2/3) * x, "R&B_Performance_Limit")

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        total_concerts = m.objVal
        return total_concerts
    else:
        return None
# Example usage
if __name__ == "__main__":
    min_concerts = optimize_concerts()
    if min_concerts is not None:
        print(f"Minimum Total Concerts: {min_concerts}")
    else:
        print("No feasible solution found.")