def solve_car_selection(participants=None, cars=None, possible_assignments=None):
    from gurobipy import Model, GRB

    # Default data based on the provided sample
    if participants is None:
        participants = ['P1', 'P2', 'P3']
    if cars is None:
        cars = ['C1', 'C2', 'C3']
    if possible_assignments is None:
        possible_assignments = [
            [1, 0, 1],  # P1 interested in C1 and C3
            [0, 1, 0],  # P2 interested in C2
            [1, 1, 1]   # P3 interested in all cars
        ]

    num_participants = len(participants)
    num_cars = len(cars)

    # Create model
    m = Model("CarSelection")
    m.setParam('OutputFlag', 0)  # Suppress output

    # Decision variables: x[i,j]
    x = m.addVars(
        range(num_participants),
        range(num_cars),
        vtype=GRB.BINARY,
        name="x"
    )

    # Objective: maximize total assignments
    m.setObjective(
        sum(x[i, j] for i in range(num_participants) for j in range(num_cars)),
        GRB.MAXIMIZE
    )

    # Constraints:
    # 1. Only assign if interested
    for i in range(num_participants):
        for j in range(num_cars):
            if possible_assignments[i][j] == 0:
                m.addConstr(x[i, j] == 0, name=f"Interest_{i}_{j}")

    # 2. Each participant assigned to at most one car
    for i in range(num_participants):
        m.addConstr(
            sum(x[i, j] for j in range(num_cars)) <= 1,
            name=f"ParticipantLimit_{i}"
        )

    # Optimize
    m.optimize()

    # Check feasibility and return the objective value
    if m.status == GRB.OPTIMAL:
        return m.objVal
    else:
        return None
if __name__ == "__main__":
    result = solve_car_selection()
    if result is not None:
        print(f"Maximum number of assignments: {result}")
    else:
        print("No feasible solution found.")