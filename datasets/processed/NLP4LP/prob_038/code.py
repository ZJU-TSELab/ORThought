def optimize_crop_allocation(
    total_land=500,
    total_water_minutes=40000,
    total_pesticide_budget=34000,
    revenue_turnips=300,
    revenue_pumpkins=450,
    watering_time_turnips=50,
    watering_time_pumpkins=90,
    pesticide_cost_turnips=80,
    pesticide_cost_pumpkins=50
):
    import gurobipy as gp
    from gurobipy import GRB

    # Create a new model
    model = gp.Model("FarmerCropOptimization")

    # Decision variables: acres of turnips and pumpkins
    x_T = model.addVar(name="Turnips", lb=0)
    x_P = model.addVar(name="Pumpkins", lb=0)

    # Set the objective: maximize total revenue
    model.setObjective(
        revenue_turnips * x_T + revenue_pumpkins * x_P,
        GRB.MAXIMIZE
    )

    # Add constraints
    # Land constraint
    model.addConstr(x_T + x_P <= total_land, name="LandLimit")
    # Watering time constraint
    model.addConstr(
        watering_time_turnips * x_T + watering_time_pumpkins * x_P <= total_water_minutes,
        name="WateringTimeLimit"
    )
    # Pesticide budget constraint
    model.addConstr(
        pesticide_cost_turnips * x_T + pesticide_cost_pumpkins * x_P <= total_pesticide_budget,
        name="PesticideBudgetLimit"
    )

    # Optimize the model
    model.optimize()

    # Check if a feasible solution was found
    if model.status == GRB.OPTIMAL:
        # Return the optimal revenue
        return model.objVal
    else:
        # No feasible solution
        return None
# Example usage
if __name__ == "__main__":
    max_revenue = optimize_crop_allocation()
    if max_revenue is not None:
        print(f"Maximum Revenue: {max_revenue}")
    else:
        print("No feasible solution found.")