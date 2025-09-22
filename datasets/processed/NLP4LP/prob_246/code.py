def optimize_catalysts(platinum_available=450, palladium_available=390):
    import gurobipy as gp
    from gurobipy import GRB

    # Create a new model
    model = gp.Model("Catalyst_Optimization")

    # Decision variables: number of each catalyst
    x = model.addVar(name="palladium_heavy", lb=0)
    y = model.addVar(name="platinum_heavy", lb=0)

    # Set the objective: maximize total CO2 conversion
    model.setObjective(5 * x + 4 * y, GRB.MAXIMIZE)

    # Add resource constraints
    model.addConstr(15 * x + 20 * y <= platinum_available, name="Platinum_Constraint")
    model.addConstr(25 * x + 14 * y <= palladium_available, name="Palladium_Constraint")

    # Optimize the model
    model.optimize()

    # Check if a feasible solution was found
    if model.status == GRB.OPTIMAL:
        return model.objVal
    else:
        return None
# Example usage
if __name__ == "__main__":
    max_conversion = optimize_catalysts()
    if max_conversion is not None:
        print(f"Maximum CO2 Conversion: {max_conversion}")
    else:
        print("No feasible solution found.")