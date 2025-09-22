def optimize_soil_bags(total_bags=150, min_topsoil=10, max_topsoil_ratio=0.3):
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("Soil_Bag_Optimization")
    
    # Decision variables: number of subsoil and topsoil bags
    x = m.addVar(vtype=GRB.INTEGER, name="subsoil_bags", lb=0)
    y = m.addVar(vtype=GRB.INTEGER, name="topsoil_bags", lb=min_topsoil)
    
    # Set the objective: minimize total water
    m.setObjective(10 * x + 6 * y, GRB.MINIMIZE)
    
    # Add constraints
    # Total bags constraint
    m.addConstr(x + y <= total_bags, "total_bags_limit")
    # Topsoil proportion constraint
    m.addConstr(y <= max_topsoil_ratio * (x + y), "topsoil_ratio")
    # Since y >= 10 is already set as lb, no need to add separately
    
    # Optimize the model
    m.optimize()
    
    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the optimal total water consumption
        return m.objVal
    else:
        # No feasible solution
        return None
# Example usage
if __name__ == "__main__":
    min_water = optimize_soil_bags()
    if min_water is not None:
        print(f"Minimum Total Water Consumption: {min_water}")
    else:
        print("No feasible solution found.")