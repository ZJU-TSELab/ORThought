def optimize_children_trip():
    from gurobipy import Model, GRB

    # Costs
    cost_Harry = 1200
    cost_Hermione = 1650
    cost_Ron = 750
    cost_Fred = 800
    cost_George = 800
    cost_Ginny = 1500  # always taken

    # Initialize model
    m = Model("Children_Trip_Optimization")
    m.setParam('OutputFlag', 0)  # suppress output

    # Decision variables
    y_Harry = m.addVar(vtype=GRB.BINARY, name='Harry')
    y_Hermione = m.addVar(vtype=GRB.BINARY, name='Hermione')
    y_Ron = m.addVar(vtype=GRB.BINARY, name='Ron')
    y_Fred = m.addVar(vtype=GRB.BINARY, name='Fred')
    y_George = m.addVar(vtype=GRB.BINARY, name='George')
    y_Ginny = 1  # always taken

    # Set objective
    m.setObjective(
        cost_Harry * y_Harry + cost_Hermione * y_Hermione + cost_Ron * y_Ron +
        cost_Fred * y_Fred + cost_George * y_George + cost_Ginny, GRB.MINIMIZE)

    # Constraints
    total_children = y_Harry + y_Hermione + y_Ron + y_Fred + y_George + y_Ginny
    m.addConstr(total_children >= 3, name='MinChildren')
    m.addConstr(total_children <= 4, name='MaxChildren')

    # Harry-Fred exclusion
    m.addConstr(y_Harry + y_Fred <= 1, name='HarryFredExcl')
    # Harry-Gorge exclusion
    m.addConstr(y_Harry + y_George <= 1, name='HarryGeorgeExcl')
    # George-Fred relationship
    m.addConstr(y_George <= y_Fred, name='GeorgeFred')
    # George-Hermione relationship
    m.addConstr(y_George <= y_Hermione, name='GeorgeHermione')

    # Optimize
    m.optimize()

    if m.status == GRB.OPTIMAL:
        return m.objVal
    else:
        return None
if __name__ == "__main__":
    result = optimize_children_trip()
    if result is not None:
        print(f"Optimal total cost for the trip: {result}")
    else:
        print("No feasible solution found.")