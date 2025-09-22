def optimize_commercials(
    budget=20000,
    cost_Pi=1200,
    reach_Pi=2000,
    cost_Beta=2000,
    reach_Beta=5000,
    cost_Gamma=4000,
    reach_Gamma=9000,
    beta_limit=8
):
    import gurobipy as gp
    from gurobipy import GRB

    # Create a new model
    model = gp.Model("Maximize Audience Reach")

    # Decision variables: number of commercials on each platform
    x_Pi = model.addVar(vtype=GRB.INTEGER, name="x_Pi", lb=0)
    x_Beta = model.addVar(vtype=GRB.INTEGER, name="x_Beta", lb=0)
    x_Gamma = model.addVar(vtype=GRB.INTEGER, name="x_Gamma", lb=0)

    # Set the objective: maximize total audience reach
    model.setObjective(
        reach_Pi * x_Pi + reach_Beta * x_Beta + reach_Gamma * x_Gamma,
        GRB.MAXIMIZE
    )

    # Budget constraint
    model.addConstr(
        cost_Pi * x_Pi + cost_Beta * x_Beta + cost_Gamma * x_Gamma <= budget,
        "Budget"
    )

    # Beta Video limit
    model.addConstr(x_Beta <= beta_limit, "BetaLimit")

    # Gamma proportion constraint: 2 * x_Gamma <= x_Pi + x_Beta
    model.addConstr(2 * x_Gamma <= x_Pi + x_Beta, "GammaProportion")

    # Pi TV minimum proportion: 4 * x_Pi >= x_Beta + x_Gamma
    model.addConstr(4 * x_Pi >= x_Beta + x_Gamma, "PiMinProportion")

    # Optimize the model
    model.optimize()

    # Check if a feasible solution was found
    if model.status == GRB.OPTIMAL:
        # Return the maximum audience reach
        return model.objVal
    else:
        # No feasible solution found
        return None
# Example usage
if __name__ == "__main__":
    max_reach = optimize_commercials()
    if max_reach is not None:
        print(f"Maximum Audience Reach: {max_reach}")
    else:
        print("No feasible solution found.")