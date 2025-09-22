def optimize_grain_transport(
    energy_limit=110,
    min_tiny_bags=20,
    large_bag_capacity=25,
    tiny_bag_capacity=6,
    energy_large=4,
    energy_tiny=1.5
):
    import gurobipy as gp
    from gurobipy import GRB

    # Create a new model
    model = gp.Model("GrainTransportMaximize")

    # Decision variables
    T = model.addVar(name="T", vtype=GRB.INTEGER, lb=min_tiny_bags)
    L = model.addVar(name="L", vtype=GRB.INTEGER, lb=0)

    # Add the bulk ratio constraint: L = 2T
    model.addConstr(L == 2 * T, name="BulkRatio")

    # Add energy constraint
    model.addConstr(energy_large * L + energy_tiny * T <= energy_limit, name="EnergyLimit")

    # Set objective: maximize total grain weight
    model.setObjective(large_bag_capacity * L + tiny_bag_capacity * T, GRB.MAXIMIZE)

    # Optimize the model
    model.optimize()

    # Check if a feasible solution was found
    if model.status == GRB.OPTIMAL:
        total_weight = model.objVal
        return total_weight
    else:
        return None
# Example usage
if __name__ == "__main__":
    max_weight = optimize_grain_transport()
    if max_weight is not None:
        print(f"Maximum Total Grain Weight: {max_weight}")
    else:
        print("No feasible solution found.")