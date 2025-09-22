import gurobipy as gp
from gurobipy import GRB


def solve_beverage_distribution(
    N=[1, 2, 3, 4, 5, 6],
    A=[(1, 2), (1, 3), (2, 3), (2, 4), (3, 5), (3, 6), (4, 5), (5, 6)],
    P=['A', 'B', 'C', 'D', 'E'],
    source=1,
    sinks=[4, 5, 6],
    u={
        (1, 2): 20, (1, 3): 15, (2, 3): 10, (2, 4): 12,
        (3, 5): 18, (3, 6): 10, (4, 5): 8, (5, 6): 15
    },
    c={
        (1, 2): 3, (1, 3): 4, (2, 3): 2, (2, 4): 5,
        (3, 5): 3, (3, 6): 6, (4, 5): 1, (5, 6): 2
    },
    d={
        (4, 'A'): 3, (4, 'B'): 2, (4, 'C'): 3,
        (5, 'B'): 4, (5, 'D'): 5, (5, 'E'): 3,
        (6, 'A'): 2, (6, 'C'): 3, (6, 'E'): 5
    },
    supply_limit=30
):
    """Solve the multi-commodity beverage distribution problem using Gurobi."""
    # Create model
    model = gp.Model("BeverageDistribution")

    # ========== Decision Variables ==========
    # Flow of product p on arc (i,j)
    x = model.addVars(A, P, lb=0, name="flow")

    # ========== Objective Function ==========
    # Minimize total transportation cost
    model.setObjective(
        gp.quicksum(c[i, j] * x[i, j, p] for (i, j) in A for p in P),
        GRB.MINIMIZE
    )

    # ========== Constraints ==========
    # 1. Flow conservation at intermediate nodes (nodes 2,3)
    for i in [2, 3]:
        for p in P:
            model.addConstr(
                gp.quicksum(x[i, j, p] for (i_, j) in A if i_ == i) -
                gp.quicksum(x[j, i, p] for (j, i_) in A if i_ == i) == 0,
                f"flow_conservation_node_{i}_product_{p}"
            )

    # 2. Demand satisfaction at sink nodes
    for i in sinks:
        for p in P:
            if (i, p) in d:
                model.addConstr(
                    gp.quicksum(x[j, i, p] for (j, i_) in A if i_ == i) -
                    gp.quicksum(x[i, j, p] for (i_, j) in A if i_ == i) == d[i, p],
                    f"demand_satisfaction_node_{i}_product_{p}"
                )
            else:
                # No demand for this product at this node
                model.addConstr(
                    gp.quicksum(x[j, i, p] for (j, i_) in A if i_ == i) -
                    gp.quicksum(x[i, j, p] for (i_, j) in A if i_ == i) == 0,
                    f"no_demand_node_{i}_product_{p}"
                )

    # 3. Arc capacity constraints
    for (i, j) in A:
        model.addConstr(
            gp.quicksum(x[i, j, p] for p in P) <= u[i, j],
            f"arc_capacity_{i}_{j}"
        )

    # 4. Source supply limit
    model.addConstr(
        gp.quicksum(x[source, j, p] for (i, j) in A if i == source for p in P) <= supply_limit,
        "source_supply_limit"
    )

    # ========== Solve the Model ==========
    model.optimize()

    # ========== Return Results ==========
    if model.status == GRB.OPTIMAL:
        return {"status": "optimal", "obj": model.ObjVal}
    else:
        return {"status": f"{model.status}"}


# Execute the function
if __name__ == "__main__":
    result = solve_beverage_distribution()
    print(result)