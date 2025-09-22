def solve_tsp(distance_matrix=None):
    from gurobipy import Model, GRB, quicksum

    # Default distance matrix based on the provided data
    if distance_matrix is None:
        distance_matrix = [[0, 86, 49, 57, 31, 69, 50],
                           [86, 0, 68, 79, 93, 24, 5],
                           [49, 68, 0, 16, 7, 72, 67],
                           [57, 79, 16, 0, 90, 69, 1],
                           [31, 93, 7, 90, 0, 86, 59],
                           [69, 24, 72, 69, 86, 0, 81],
                           [50, 5, 67, 1, 59, 81, 0]]

    n = len(distance_matrix)
    model = Model()

    # Decision variables: x[i,j] binary
    x = {}
    for i in range(n):
        for j in range(n):
            if i != j:
                x[i, j] = model.addVar(vtype=GRB.BINARY, name=f"x_{i}_{j}")

    # MTZ variables for subtour elimination
    u = {}
    for i in range(1, n):
        u[i] = model.addVar(lb=2, ub=n, vtype=GRB.CONTINUOUS, name=f"u_{i}")

    model.update()

    # Objective: minimize total distance
    model.setObjective(
        quicksum(distance_matrix[i][j] * x[i, j] for i in range(n)
                 for j in range(n) if i != j), GRB.MINIMIZE)

    # Constraints:

    # 1. From start location (0), exactly one outgoing edge
    model.addConstr(quicksum(x[0, j] for j in range(1, n)) == 1,
                    name="start_out")

    # 2. Each node (except start) has exactly one incoming edge
    for j in range(1, n):
        model.addConstr(quicksum(x[i, j] for i in range(n) if i != j) == 1,
                        name=f"node_in_{j}")

    # 3. Each node (except start) has exactly one outgoing edge
    for i in range(1, n):
        model.addConstr(quicksum(x[i, j] for j in range(n) if j != i) == 1,
                        name=f"node_out_{i}")

    # 4. Subtour elimination (MTZ)
    for i in range(1, n):
        for j in range(1, n):
            if i != j:
                model.addConstr(u[i] - u[j] + n * x[i, j] <= n - 1,
                                name=f"subtour_{i}_{j}")

    # Optimize
    model.optimize()

    # Check feasibility
    if model.status == GRB.OPTIMAL:
        return model.objVal
    else:
        return None
if __name__ == "__main__":
    result = solve_tsp()
    if result is not None:
        print(f"Optimal total distance: {result}")
    else:
        print("No feasible solution found.")