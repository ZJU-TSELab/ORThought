def optimize_printers():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("Printer_Optimization")

    # Decision variables: number of premium and regular printers
    x = m.addVar(vtype=GRB.INTEGER, name="Premium")
    y = m.addVar(vtype=GRB.INTEGER, name="Regular")

    # Set objective: minimize total number of printers
    m.setObjective(x + y, GRB.MINIMIZE)

    # Add constraints
    # Printing capacity constraint
    m.addConstr(30 * x + 20 * y >= 200, name="PrintCapacity")
    # Ink usage constraint
    m.addConstr(4 * x + 3 * y <= 35, name="InkLimit")
    # Preference constraint: y < x
    m.addConstr(y <= x - 1, name="Preference")
    # Non-negativity constraints are implicit in variable definitions

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the total number of printers in the optimal solution
        total_printers = x.X + y.X
        return total_printers
    else:
        # No feasible solution found
        return None
# Example usage
if __name__ == "__main__":
    min_printers = optimize_printers()
    if min_printers is not None:
        print(f"Minimum Total Number of Printers: {min_printers}")
    else:
        print("No feasible solution found.")