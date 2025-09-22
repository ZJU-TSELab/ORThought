def optimize_souvenirs():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("Souvenir_Production")

    # Decision variables: number of elephants and tigers
    # Both are integers and non-negative
    x = m.addVar(vtype=GRB.INTEGER, name="Elephants", lb=0)
    y = m.addVar(vtype=GRB.INTEGER, name="Tigers", lb=0)

    # Set the objective: maximize profit
    m.setObjective(5 * x + 4 * y, GRB.MAXIMIZE)

    # Add resource constraints
    m.addConstr(50 * x + 40 * y <= 5000, "WoodConstraint")
    m.addConstr(20 * x + 30 * y <= 4000, "PlasticConstraint")

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
    max_profit = optimize_souvenirs()
    if max_profit is not None:
        print(f"Maximum Profit: {max_profit}")
    else:
        print("No feasible solution found.")