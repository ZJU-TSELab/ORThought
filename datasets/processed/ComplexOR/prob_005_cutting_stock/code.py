def solve_cutting_stock(RollWidth=10, widths=[2, 3, 5], orders=[4, 2, 2], num_patterns=2, num_rolls_width=[[1, 2, 0], [0, 0, 1]]):
    import gurobipy as gp
    from gurobipy import GRB

    num_widths = len(widths)
    num_patterns = len(num_rolls_width)

    # Create a new model
    model = gp.Model("CuttingStock")

    # Decision variables: number of rolls cut using each pattern
    y = model.addVars(range(num_patterns), vtype=GRB.INTEGER, lb=0, name="y")

    # Objective: minimize total number of raw rolls used
    model.setObjective(gp.quicksum(y[j] for j in range(num_patterns)), GRB.MINIMIZE)

    # Constraints: meet or exceed each order
    for i in range(num_widths):
        model.addConstr(
            gp.quicksum(num_rolls_width[j][i] * y[j] for j in range(num_patterns)) >= orders[i],
            name=f"Width_{i}"
        )

    # Optimize the model
    model.optimize()

    # Check if a feasible solution was found
    if model.status == GRB.OPTIMAL:
        total_rolls = sum(y[j].X for j in range(num_patterns))
        return total_rolls
    else:
        return None
if __name__ == "__main__":
    result = solve_cutting_stock()
    if result is not None:
        print(f"Minimum number of rolls used: {result}")
    else:
        print("No feasible solution found.")