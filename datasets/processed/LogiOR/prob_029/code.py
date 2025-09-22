import gurobipy as gp
from gurobipy import GRB


def solve_container_optimization(
    volumes=[17, 19, 21, 23, 25, 29, 33],
    demands=[500, 400, 300, 250, 200, 150, 100],
    fixed_cost=1000):
    """
    Solves the container production and assignment optimization problem.
    """
    # --- 1. Model Creation ---
    model = gp.Model("Container_Optimization")

    # --- 2. Parameters & Sets ---
    container_types = range(len(volumes))
    variable_costs = volumes  # Variable cost equals volume

    # --- 3. Decision Variables ---
    # produce[j] = 1 if container type j is produced, 0 otherwise
    produce = model.addVars(container_types, vtype=GRB.BINARY, name="Produce")

    # assign[i, j] = number of units of demand type i satisfied by container type j
    assign_keys = [(i, j) for i in container_types for j in container_types
                   if j >= i]
    assign = model.addVars(assign_keys, vtype=GRB.INTEGER, name="Assign")

    # --- 4. Objective Function ---
    # Minimize total cost (fixed production costs + variable assignment costs)
    total_cost = gp.quicksum(fixed_cost * produce[j]
                             for j in container_types) + \
                 gp.quicksum(variable_costs[j] * assign[i, j]
                             for i, j in assign_keys)
    model.setObjective(total_cost, GRB.MINIMIZE)

    # --- 5. Constraints ---
    # Demand satisfaction: All demand for type i must be met.
    model.addConstrs(
        (assign.sum(i, '*') == demands[i] for i in container_types),
        name="Demand")

    # Production activation: If any containers of type j are used, we must incur the fixed cost.
    M = sum(demands)  # Big-M: an upper bound on the total number of containers of one type
    model.addConstrs(
        (assign.sum('*', j) <= M * produce[j] for j in container_types),
        name="Activation")

    # --- 6. Solve the Model ---
    model.optimize()

    # --- 7. Return Results ---
    if model.status == GRB.OPTIMAL:
        return {"status": "optimal", "obj": model.ObjVal}
    else:
        return {"status": f"{model.status}"}


if __name__ == "__main__":
    result = solve_container_optimization()
    print(result)