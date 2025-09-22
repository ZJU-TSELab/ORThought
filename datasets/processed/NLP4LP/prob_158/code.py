def optimize_animals():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("Animal_Optimization")

    # Decision variables
    C = m.addVar(vtype=GRB.INTEGER, name="Camels", lb=0)
    H = m.addVar(vtype=GRB.INTEGER, name="Horses", lb=0)

    # Set objective: minimize total number of animals
    m.setObjective(C + H, GRB.MINIMIZE)

    # Add constraints
    # Package capacity constraint
    m.addConstr(50 * C + 60 * H >= 1000, name="PackageCapacity")
    # Food constraint
    m.addConstr(20 * C + 30 * H <= 450, name="FoodLimit")
    # Horse-to-camel ratio
    m.addConstr(H <= C, name="HorseCamelRatio")

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        total_animals = m.objVal
        return total_animals
    else:
        return None
# Example usage
if __name__ == "__main__":
    min_animals = optimize_animals()
    if min_animals is not None:
        print(f"Minimum Total Animals (Camels + Horses): {min_animals}")
    else:
        print("No feasible solution found.")