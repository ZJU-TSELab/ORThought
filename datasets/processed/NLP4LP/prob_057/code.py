def optimize_bottles(max_syrup_ml=25000, min_kids_bottles=50):
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("CoughSyrupBottles")

    # Decision variables: number of kids and adult bottles
    x = m.addVar(vtype=GRB.INTEGER, name="kids_bottles")
    y = m.addVar(vtype=GRB.INTEGER, name="adult_bottles")

    # Set the objective: maximize total bottles
    m.setObjective(x + y, GRB.MAXIMIZE)

    # Add constraints
    # Volume constraint
    m.addConstr(100 * x + 300 * y <= max_syrup_ml, "volume_constraint")
    # Minimum kids bottles
    m.addConstr(x >= min_kids_bottles, "min_kids")
    # Adult bottles at least three times kids
    m.addConstr(y >= 3 * x, "adult_kids_ratio")

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        total_bottles = m.objVal
        return total_bottles
    else:
        return None
# Example usage
if __name__ == "__main__":
    max_bottles = optimize_bottles()
    if max_bottles is not None:
        print(f"Maximum Total Bottles: {max_bottles}")
    else:
        print("No feasible solution found.")