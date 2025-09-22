def optimize_bouquets():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("FlowerBouquets")

    # Decision variables
    S = m.addVar(vtype=GRB.INTEGER, name="SmallBouquets")
    L = m.addVar(vtype=GRB.INTEGER, name="LargeBouquets")

    # Set objective: maximize total flowers
    m.setObjective(5 * S + 10 * L, GRB.MAXIMIZE)

    # Add constraints
    m.addConstr(S <= 80, name="MaxSmall")
    m.addConstr(L <= 50, name="MaxLarge")
    m.addConstr(S + L <= 70, name="TotalBouquets")
    m.addConstr(L >= 20, name="MinLarge")
    m.addConstr(S >= 2 * L, name="SmallAtLeastTwiceLarge")
    m.addConstr(S >= 0, name="NonNegSmall")
    m.addConstr(L >= 0, name="NonNegLarge")

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the maximum total number of flowers
        return m.objVal
    else:
        # No feasible solution
        return None
# Example usage
if __name__ == "__main__":
    max_flowers = optimize_bouquets()
    if max_flowers is not None:
        print(f"Maximum Total Flowers: {max_flowers}")
    else:
        print("No feasible solution found.")