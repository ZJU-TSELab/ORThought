def optimize_paste(max_water=500, max_powder=700):
    import gurobipy as gp
    from gurobipy import GRB

    # Create a new model
    model = gp.Model("pharmaceutical_paste")

    # Decision variables: number of small and large containers
    x = model.addVar(vtype=GRB.INTEGER, name="small_container")
    y = model.addVar(vtype=GRB.INTEGER, name="large_container")

    # Set the objective: maximize total paste
    model.setObjective(20 * x + 30 * y, GRB.MAXIMIZE)

    # Add resource constraints
    model.addConstr(10 * x + 20 * y <= max_water, "water_constraint")
    model.addConstr(15 * x + 20 * y <= max_powder, "powder_constraint")

    # Optimize the model
    model.optimize()

    # Check if a feasible solution was found
    if model.status == GRB.OPTIMAL:
        # Return the maximum total paste produced
        return model.objVal
    else:
        # No feasible solution found
        return None
# Example usage
if __name__ == "__main__":
    max_paste = optimize_paste()
    if max_paste is not None:
        print(f"Maximum Total Paste Produced: {max_paste}")
    else:
        print("No feasible solution found.")