def optimize_project_assignment(
    supply={'value': [8, 7], 'description': 'list, hours each person is available'},
    demand={'value': [5, 10], 'description': 'list, hours each project requires'},
    cost={'value': [[10, 20], [15, 25]], 'description': 'cost per hour for each person on each project'},
    limit={'value': [[5, 6], [4, 7]], 'description': 'max contribution per person-project'}
):
    import gurobipy as gp
    from gurobipy import GRB

    num_people = len(supply['value'])
    num_projects = len(demand['value'])

    # Create model
    model = gp.Model("ProjectAssignment")

    # Decision variables: x[i,j]
    x = model.addVars(
        range(num_people),
        range(num_projects),
        lb=0,
        ub=GRB.INFINITY,
        name="x"
    )

    # Set the objective: minimize total cost
    obj = gp.quicksum(
        cost['value'][i][j] * x[i, j]
        for i in range(num_people)
        for j in range(num_projects)
    )
    model.setObjective(obj, GRB.MINIMIZE)

    # Supply constraints: sum over projects for each person
    for i in range(num_people):
        model.addConstr(
            gp.quicksum(x[i, j] for j in range(num_projects)) == supply['value'][i],
            name=f"Supply_{i}"
        )

    # Demand constraints: sum over people for each project
    for j in range(num_projects):
        model.addConstr(
            gp.quicksum(x[i, j] for i in range(num_people)) == demand['value'][j],
            name=f"Demand_{j}"
        )

    # Limit constraints: x[i,j] <= limit[i][j]
    for i in range(num_people):
        for j in range(num_projects):
            model.addConstr(
                x[i, j] <= limit['value'][i][j],
                name=f"Limit_{i}_{j}"
            )

    # Optimize the model
    model.optimize()

    # Check if a feasible solution was found
    if model.status == GRB.OPTIMAL:
        # Return the optimal total cost
        return model.objVal
    else:
        # No feasible solution
        return None
if __name__ == "__main__":
    result = optimize_project_assignment()
    if result is not None:
        print(f"Minimum total cost: {result}")
    else:
        print("No feasible solution found.")