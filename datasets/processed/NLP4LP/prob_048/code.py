def optimize_bubble_tea(minimize_tea=True):
    from gurobipy import Model, GRB, quicksum

    # Create a new model
    model = Model("BubbleTeaOptimization")
    model.setParam('OutputFlag', 0)  # Suppress Gurobi output

    # Decision variables: number of mango and lychee bubble teas
    x_m = model.addVar(vtype=GRB.INTEGER, name='x_m', lb=0)
    x_l = model.addVar(vtype=GRB.INTEGER, name='x_l', lb=0)

    # Add constraints
    # Juice constraints
    model.addConstr(4 * x_m <= 2000, name='mango_juice')
    model.addConstr(6 * x_l <= 3000, name='lychee_juice')
    # Total tea constraint
    model.addConstr(8 * x_m + 6 * x_l <= 3000, name='total_tea')
    # Lychee proportion constraint
    model.addConstr(3 * x_l >= 2 * x_m, name='lychee_ratio')
    # Mango more than lychee
    model.addConstr(x_m >= x_l + 1, name='mango_more_than_lychee')

    # Objective: minimize total tea
    model.setObjective(8 * x_m + 6 * x_l, GRB.MINIMIZE)

    # Optimize
    model.optimize()

    # Check if a feasible solution was found
    if model.status == GRB.OPTIMAL:
        total_tea = model.objVal
        return total_tea
    else:
        return None
# Example usage
if __name__ == "__main__":
    min_tea = optimize_bubble_tea()
    if min_tea is not None:
        print(f"Minimum Total Tea: {min_tea}")
    else:
        print("No feasible solution found.")