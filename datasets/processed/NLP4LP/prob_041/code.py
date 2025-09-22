def optimize_stores():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("Minimize_Stores")

    # Decision variables: number of dine-in stores and food-trucks
    x = m.addVar(vtype=GRB.INTEGER, name="dine_in")
    y = m.addVar(vtype=GRB.INTEGER, name="food_truck")

    # Set the objective: minimize total number of stores
    m.setObjective(x + y, GRB.MINIMIZE)

    # Add constraints
    # Sandwich production constraint
    m.addConstr(100 * x + 50 * y >= 500, "sandwich_requirement")
    # Employee constraint
    m.addConstr(8 * x + 3 * y <= 35, "employee_limit")
    # Non-negativity constraints are implicit in variable definitions

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the optimal total number of stores
        return m.objVal
    else:
        # No feasible solution found
        return None
# Example usage
if __name__ == "__main__":
    min_stores = optimize_stores()
    if min_stores is not None:
        print(f"Minimum Number of Stores: {min_stores}")
    else:
        print("No feasible solution found.")