def optimize_crude_processing(
    revenue_light=550,
    revenue_non_sticky=750,
    revenue_heavy=950,
    compound_A_total=250,
    compound_B_total=150
):
    import gurobipy as gp
    from gurobipy import GRB

    # Create a new model
    model = gp.Model("CrudeOilProcessing")

    # Decision variables: number of tanks processed for each oil type
    x_L = model.addVar(name="LightOil", lb=0)
    x_N = model.addVar(name="NonStickyOil", lb=0)
    x_H = model.addVar(name="HeavyOil", lb=0)

    # Set the objective: maximize total revenue
    model.setObjective(
        revenue_light * x_L + revenue_non_sticky * x_N + revenue_heavy * x_H,
        GRB.MAXIMIZE
    )

    # Add resource constraints
    # Compound A constraint
    model.addConstr(
        3 * x_L + 6 * x_N + 9 * x_H <= compound_A_total,
        name="CompoundA"
    )

    # Compound B constraint
    model.addConstr(
        3 * x_L + 2 * x_N + 3 * x_H <= compound_B_total,
        name="CompoundB"
    )

    # Optimize the model
    model.optimize()

    # Check if a feasible solution was found
    if model.status == GRB.OPTIMAL:
        return model.objVal
    else:
        return None
# Example usage
if __name__ == "__main__":
    max_revenue = optimize_crude_processing()
    if max_revenue is not None:
        print(f"Maximum Revenue: ${max_revenue}")
    else:
        print("No feasible solution found.")