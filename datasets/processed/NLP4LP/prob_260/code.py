def optimize_factory_hours(
    injection_target=800000,
    cream_target=700000,
    plastic_limit=60000,
    rate_injection_north=800,
    rate_cream_north=700,
    rate_injection_west=650,
    rate_cream_west=750,
    plastic_north=40,
    plastic_west=35
):
    import gurobipy as gp
    from gurobipy import GRB

    # Create a new model
    model = gp.Model("Factory_Production_MinHours")

    # Decision variables: hours of operation for each factory
    x_N = model.addVar(name="x_N", lb=0)
    x_W = model.addVar(name="x_W", lb=0)
    max_hour = model.addVar(name="max_hour", lb=0)

    # Set the objective: minimize total hours
    model.setObjective(max_hour, GRB.MINIMIZE)

    # Add constraints
    # Anti-itch injections production constraint
    model.addConstr(
        rate_injection_north * x_N + rate_injection_west * x_W >= injection_target,
        name="InjectionRequirement"
    )

    # Topical cream production constraint
    model.addConstr(
        rate_cream_north * x_N + rate_cream_west * x_W >= cream_target,
        name="CreamRequirement"
    )

    # Plastic usage constraint
    model.addConstr(
        plastic_north * x_N + plastic_west * x_W <= plastic_limit,
        name="PlasticLimit"
    )
    
    # Maximum hours constraint
    model.addConstr(max_hour >= x_N, name="MaxHour_N")
    model.addConstr(max_hour >= x_W, name="MaxHour_W")
    
    # Optimize the model
    model.optimize()

    # Check if a feasible solution was found
    if model.status == GRB.OPTIMAL:
        total_hours = model.objVal
        return total_hours
    else:
        return None
    
# Example usage
print(optimize_factory_hours())