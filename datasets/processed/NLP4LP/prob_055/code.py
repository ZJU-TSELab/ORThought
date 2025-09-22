def optimize_croissants(butter_available=600, flour_available=800,
                        time_almond=12, time_pistachio=10,
                        butter_almond=5, flour_almond=8,
                        butter_pistachio=3, flour_pistachio=6):
    import gurobipy as gp
    from gurobipy import GRB

    # Create a new model
    model = gp.Model("Croissant_Production_MinTime")

    # Decision variables: number of croissants
    x = model.addVar(vtype=GRB.INTEGER, name="AlmondCroissants", lb=0)
    y = model.addVar(vtype=GRB.INTEGER, name="PistachioCroissants", lb=0)

    # Set objective: minimize total production time
    model.setObjective(time_almond * x + time_pistachio * y, GRB.MINIMIZE)

    # Add resource constraints
    model.addConstr(butter_almond * x + butter_pistachio * y <= butter_available, "ButterLimit")
    model.addConstr(flour_almond * x + flour_pistachio * y <= flour_available, "FlourLimit")

    # Add popularity constraint
    model.addConstr(x >= 3 * y, "PopularityConstraint")

    # Optimize the model
    model.optimize()

    # Check if a feasible solution was found
    if model.status == GRB.OPTIMAL:
        # Return the total minimized time
        return model.objVal
    else:
        # No feasible solution
        return None
# Example usage
if __name__ == "__main__":
    min_time = optimize_croissants()
    if min_time is not None:
        print(f"Minimum Total Production Time: {min_time}")
    else:
        print("No feasible solution found.")