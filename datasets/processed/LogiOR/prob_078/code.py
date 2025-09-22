import gurobipy as gp
from gurobipy import GRB
import math


def solve_shipping_problem(
    routes=[1, 2, 3, 4, 5, 6],
    ships=list(range(1, 11)),
    RouteDemand={
        1: 6500,
        2: 7200,
        3: 4800,
        4: 5100,
        5: 6200,
        6: 3900
    },
    Revenue={
        1: 120,
        2: 150,
        3: 90,
        4: 110,
        5: 140,
        6: 80
    },
    Distance={
        1: 1200,
        2: 1800,
        3: 900,
        4: 1200,
        5: 1800,
        6: 900
    },
    ShipCapacity=8000,
    FuelConsumptionRate=0.2,
    FuelCost=600,
    MinLoadPercentage=0.7
):
    # Create model
    model = gp.Model("Shipping_Optimization")

    # Decision variables
    # Binary variable: 1 if ship s is assigned to route r
    x = model.addVars(ships, routes, vtype=GRB.BINARY, name="assign")

    # Continuous variable: total containers shipped on route r
    y = model.addVars(routes, lb=0, vtype=GRB.CONTINUOUS, name="containers")

    # Objective function: maximize profit (revenue - fuel costs)
    revenue = gp.quicksum(Revenue[r] * y[r] for r in routes)
    fuel_cost = gp.quicksum(
        x[s, r] * Distance[r] * FuelConsumptionRate * FuelCost
        for s in ships for r in routes
    )
    model.setObjective(revenue - fuel_cost, GRB.MAXIMIZE)

    # Constraints
    # 1. Demand satisfaction
    model.addConstrs(
        (y[r] >= RouteDemand[r] for r in routes),
        name="demand_satisfaction"
    )

    # 2. Ship capacity constraints
    model.addConstrs(
        (y[r] <= gp.quicksum(x[s, r] for s in ships) * ShipCapacity for r in routes),
        name="capacity_limit"
    )

    # 3. Minimum loading requirement (70% of capacity)
    model.addConstrs(
        (y[r] >= gp.quicksum(x[s, r] for s in ships) * ShipCapacity * MinLoadPercentage for r in routes),
        name="min_loading"
    )

    # 4. Each ship can be assigned to at most 1 route
    model.addConstrs(
        (gp.quicksum(x[s, r] for r in routes) <= 1 for s in ships),
        name="ship_assignment_limit"
    )

    # 5. Maximum ships per route (ceil(demand/capacity))
    max_ships_per_route = {
        r: math.ceil(RouteDemand[r] / ShipCapacity) for r in routes
    }
    model.addConstrs(
        (gp.quicksum(x[s, r] for s in ships) <= max_ships_per_route[r] for r in routes),
        name="max_ships_per_route"
    )

    # 6. Total ship usage cannot exceed available ships (10)
    model.addConstr(
        gp.quicksum(x[s, r] for s in ships for r in routes) <= 10,
        name="total_ship_usage"
    )

    # Optimize the model
    model.optimize()

    # Return results
    if model.status == GRB.OPTIMAL:
        return {"status": "optimal", "obj": model.ObjVal}
    else:
        return {"status": f"{model.status}"}


if __name__ == "__main__":
    result = solve_shipping_problem()
    print(result)