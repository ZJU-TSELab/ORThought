def optimize_honey_jars():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("HoneyJarsMaximize")

    # Decision variables
    G = m.addVar(name="GlassJars", vtype=GRB.INTEGER, lb=20)  # at least 20 glass jars
    P = m.addVar(name="PlasticJars", vtype=GRB.INTEGER, lb=0)

    # Set objective: maximize total number of jars
    m.setObjective(G + P, GRB.MAXIMIZE)

    # Add constraints
    # Honey volume constraint
    m.addConstr(250 * G + 300 * P <= 20000, name="HoneyVolume")
    # Relationship constraint
    m.addConstr(P >= 2 * G, name="PlasticAtLeastTwiceGlass")
    # Non-negativity is enforced by lb=0 for P and lb=20 for G

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the maximum total number of jars filled
        return m.objVal
    else:
        # No feasible solution
        return None
# Example usage
if __name__ == "__main__":
    max_jars = optimize_honey_jars()
    if max_jars is not None:
        print(f"Maximum Total Jars Filled: {max_jars}")
    else:
        print("No feasible solution found.")