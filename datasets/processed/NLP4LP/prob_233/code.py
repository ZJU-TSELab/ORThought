def optimize_equipment_purchase():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("Equipment_Purchase")

    # Decision variables: number of chop saws (x) and steel cutters (y)
    x = m.addVar(vtype=GRB.INTEGER, name="chop_saws", lb=0)
    y = m.addVar(vtype=GRB.INTEGER, name="steel_cutters", lb=0)

    # Set the objective: minimize total equipment
    m.setObjective(x + y, GRB.MINIMIZE)

    # Add demand constraint
    m.addConstr(25 * x + 5 * y >= 520, name="demand_constraint")

    # Add waste constraint
    m.addConstr(25 * x + 3 * y <= 400, name="waste_constraint")

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the optimal total number of equipment
        return m.objVal
    else:
        # No feasible solution found
        return None
# Example usage
if __name__ == "__main__":
    min_equipment = optimize_equipment_purchase()
    if min_equipment is not None:
        print(f"Minimum Total Equipment (Chop Saws + Steel Cutters): {min_equipment}")
    else:
        print("No feasible solution found.")