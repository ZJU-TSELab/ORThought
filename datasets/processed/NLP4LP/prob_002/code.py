def optimize_ad_campaign(
    budget=250000,
    radio_cost=5000,
    social_media_cost=9150,
    exposure_radio=60500,
    exposure_social=50000,
    min_radio=15,
    max_radio=40,
    min_social=35
):
    import gurobipy as gp
    from gurobipy import GRB

    # Create a new model
    model = gp.Model("AdCampaignOptimization")

    # Decision variables
    R = model.addVar(vtype=GRB.INTEGER, name="RadioAds")
    S = model.addVar(vtype=GRB.INTEGER, name="SocialMediaAds")

    # Set objective: maximize total exposure
    model.setObjective(
        exposure_radio * R + exposure_social * S,
        GRB.MAXIMIZE
    )

    # Add constraints
    # Budget constraint
    model.addConstr(
        radio_cost * R + social_media_cost * S <= budget,
        name="BudgetConstraint"
    )

    # Radio ads bounds
    model.addConstr(R >= min_radio, name="MinRadioAds")
    model.addConstr(R <= max_radio, name="MaxRadioAds")

    # Social media ads minimum
    model.addConstr(S >= min_social, name="MinSocialMediaAds")

    # Optimize the model
    model.optimize()

    # Check if a feasible solution was found
    if model.status == GRB.OPTIMAL:
        total_exposure = model.objVal
        return total_exposure
    else:
        return None
# Example usage
if __name__ == "__main__":
    max_exposure = optimize_ad_campaign()
    if max_exposure is not None:
        print(f"Maximum Total Exposure: {max_exposure}")
    else:
        print("No feasible solution found.")