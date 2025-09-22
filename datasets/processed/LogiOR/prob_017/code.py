import gurobipy as gp
from gurobipy import GRB
import math


def solve_tsp(
    coordinates=[(0, 0), (3.5, 4.2), (-2.1, 5.6), (4.8, -3.2), (-3.6, -2.8),
                 (5.2, 2.4), (-4.1, 3.7), (2.8, -4.5), (6.3, -2.1),
                 (-5.2, -1.8), (3.9, 5.8)]):
    """
    Solves the Traveling Salesperson Problem (TSP) for community health services.
    """
    community_num = len(coordinates) - 1
    nodes = range(community_num + 1
                  )  # 0 is the central hospital, 1-10 are communities

    # Calculate distance matrix
    def calculate_distance(coord1, coord2):
        return math.sqrt((coord1[0] - coord2[0])**2 +
                         (coord1[1] - coord2[1])**2)

    distance = {}
    for i in nodes:
        for j in nodes:
            if i != j:
                distance[i,
                         j] = calculate_distance(coordinates[i], coordinates[j])

    # Create a new model
    model = gp.Model("TSP")

    # Decision variables: x[i,j] = 1 if the path goes from i to j
    x = {}
    for i in nodes:
        for j in nodes:
            if i != j:
                x[i, j] = model.addVar(vtype=GRB.BINARY, name=f'x_{i}_{j}')

    # Set objective: minimize total distance
    objective = gp.quicksum(distance[i, j] * x[i, j] for i in nodes
                            for j in nodes if i != j)
    model.setObjective(objective, GRB.MINIMIZE)

    # Constraint 1: Each node must be visited exactly once
    for j in nodes:
        model.addConstr(gp.quicksum(x[i, j] for i in nodes if i != j) == 1,
                        name=f'visit_to_{j}')

    # Constraint 2: Must leave each node exactly once
    for i in nodes:
        model.addConstr(gp.quicksum(x[i, j] for j in nodes if i != j) == 1,
                        name=f'leave_from_{i}')

    # Constraint 3: Subtour elimination using subset constraints
    def find_subtours(edges):
        # Create adjacency list
        adj = {i: [] for i in nodes}
        for i, j in edges:
            adj[i].append(j)

        # Find all subtours
        unvisited = set(nodes)
        subtours = []
        while unvisited:
            # Start from any unvisited node
            current = next(iter(unvisited))
            subtour = []
            while current in unvisited:
                unvisited.remove(current)
                subtour.append(current)
                # Move to next node in path
                next_nodes = adj.get(current, [])
                if not next_nodes:
                    break
                current = next_nodes[0]
            if len(subtour) < len(nodes):
                subtours.append(subtour)
        return subtours

    # Callback function for lazy constraints
    def subtour_cb(model, where):
        if where == GRB.Callback.MIPSOL:
            # Get values of decision variables
            x_vals = model.cbGetSolution(model._vars)
            edges = [(i, j) for i in nodes for j in nodes
                     if i != j and x_vals[i, j] > 0.5]

            # Find subtours
            subtours = find_subtours(edges)

            # Add subtour elimination constraints
            for S in subtours:
                if len(S) < len(nodes):
                    model.cbLazy(
                        gp.quicksum(x[i, j] for i in S for j in S
                                    if i != j) <= len(S) - 1)

    # Enable lazy constraints
    model._vars = x
    model.Params.lazyConstraints = 1

    # Optimize model with callback
    model.optimize(subtour_cb)

    # Return results
    if model.status == GRB.OPTIMAL:
        return {"status": "optimal", "obj": model.ObjVal}
    else:
        return {"status": f"{model.status}"}


# Run the solver function
if __name__ == "__main__":
    result = solve_tsp()
    print(result)
