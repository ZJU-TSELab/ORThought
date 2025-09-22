import gurobipy as gp
from gurobipy import GRB


def solve_logistics(
    routes=["Route1", "Route2", "Route3"],
    total_tonnage_to_ship=1000.0,
    linear_cost_per_ton={
        "Route1": 700,
        "Route2": 1085,
        "Route3": 670
    },
    congestion_coeff={
        "Route1": 5e-7,
        "Route2": 8e-7,
        "Route3": 0
    },
    background_traffic={
        "Route1": 2000,
        "Route2": 1500,
        "Route3": 0
    }
):
    """
    Solves the transportation logistics problem with congestion pricing.
    """
    # Create a new model
    model = gp.Model("LogisticsOptimization")

    # --- Decision Variables ---
    # Amount of goods to ship on each route (in tons)
    tonnage_on_route = model.addVars(routes, name="TonnageOnRoute", lb=0)

    # --- Objective Function: Minimize Total Transportation Cost ---
    # Linear cost component
    total_linear_cost = gp.quicksum(
        linear_cost_per_ton[r] * tonnage_on_route[r] for r in routes
    )

    # Congestion cost component (this makes the objective quadratic)
    total_congestion_cost = gp.quicksum(
        congestion_coeff[r] *
        (background_traffic[r] + tonnage_on_route[r]) *
        (background_traffic[r] + tonnage_on_route[r])
        for r in routes if congestion_coeff[r] > 0
    )

    # Set the complete objective function
    model.setObjective(total_linear_cost + total_congestion_cost, GRB.MINIMIZE)

    # --- Constraints ---
    # 1. Total Tonnage Constraint: Must ship the exact total amount of goods
    model.addConstr(
        tonnage_on_route.sum('*') == total_tonnage_to_ship,
        name="TotalTonnageRequirement"
    )

    # Optimize the model
    model.optimize()

    # --- Return Results ---
    if model.status == GRB.OPTIMAL:
        return {"status": "optimal", "obj": model.objVal}
    else:
        return {"status": f"{model.status}"}


# Run the solver function
if __name__ == '__main__':
    result = solve_logistics()
    print(result)