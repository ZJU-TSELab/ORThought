def optimize_mask_boxes():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("mask_box_optimization")

    # Decision variables
    # Number of small boxes
    x = m.addVar(vtype=GRB.INTEGER, name="small_boxes")
    # Number of large boxes
    y = m.addVar(vtype=GRB.INTEGER, name="large_boxes")

    # Set objective: minimize total number of boxes
    m.setObjective(x + y, GRB.MINIMIZE)

    # Add constraints
    # Mask capacity constraint
    m.addConstr(25 * x + 45 * y >= 750, name="mask_capacity")
    # Ratio constraint: small boxes at least three times large boxes
    m.addConstr(x >= 3 * y, name="ratio_constraint")
    # Minimum large boxes
    m.addConstr(y >= 5, name="min_large_boxes")
    # Non-negativity is implicit in variable type (integer >= 0)

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        total_boxes = m.objVal
        small_boxes = x.X
        large_boxes = y.X
        return total_boxes
    else:
        # No feasible solution found
        return None
# Example usage
if __name__ == "__main__":
    min_boxes = optimize_mask_boxes()
    if min_boxes is not None:
        print(f"Minimum Total Boxes: {min_boxes}")
    else:
        print("No feasible solution found.")