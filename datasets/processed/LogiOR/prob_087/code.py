import gurobipy as gp
from gurobipy import GRB
import math

def solve_profitable_taxi_dispatch(
    areas=["A1", "A2", "A3"],
    hotspots=["H1", "H2", "H3"],
    demand={"H1": 30, "H2": 50, "H3": 40},
    available_taxis={"A1": 25, "A2": 40, "A3": 35},
    base_fare=15.0,
    deadheading_costs_data={
        ("A1", "H1"): 16, ("A1", "H2"): 28, ("A1", "H3"): 24,
        ("A2", "H1"): 20, ("A2", "H2"): 12, ("A2", "H3"): 32,
        ("A3", "H1"): 24, ("A3", "H2"): 20, ("A3", "H3"): 16,
    }
):
    """
    Solves the adjusted (profitable) taxi dispatch optimization problem using Gurobi.
    This model includes a base fare and reduced deadheading costs.
    """
    # Create a new model
    model = gp.Model("ProfitableTaxiDispatch")

    deadheading_costs = gp.tupledict(deadheading_costs_data)

    # --- Decision Variables ---
    # dispatch_plan[i, j]: Number of taxis dispatched from area i to hotspot j
    dispatch_plan = model.addVars(areas, hotspots, vtype=GRB.INTEGER, name="DispatchPlan", lb=0)

    # supply[j]: Total number of taxis arriving at hotspot j
    supply = model.addVars(hotspots, name="Supply", lb=0)
    
    # revenue_calc_surcharge[j]: Auxiliary variable for the non-linear surcharge revenue term, representing supply[j]^1.5
    revenue_calc_surcharge = model.addVars(hotspots, name="SurchargeRevenueCalc", lb=0)

    # --- Objective Function: Maximize Total Profit ---
    total_base_fare_revenue = base_fare * gp.quicksum(supply[j] for j in hotspots)
    
    total_surcharge_revenue = math.sqrt(2) * gp.quicksum(revenue_calc_surcharge[j] for j in hotspots)

    total_revenue = total_base_fare_revenue + total_surcharge_revenue

    total_deadheading_cost = dispatch_plan.prod(deadheading_costs)

    model.setObjective(total_revenue - total_deadheading_cost, GRB.MAXIMIZE)

    # --- Constraints ---
    # 1. Supply definition constraint
    for j in hotspots:
        model.addConstr(supply[j] == gp.quicksum(dispatch_plan[i, j] for i in areas),
                        name=f"SupplyDef_{j}")

    # 2. Surcharge revenue calculation (non-linear power constraint)
    for j in hotspots:
        model.addGenConstrPow(supply[j], revenue_calc_surcharge[j], 1.5, name=f"RevenuePow_{j}")

    # 3. Hotspot demand constraint
    for j in hotspots:
        model.addConstr(supply[j] <= demand[j], name=f"Demand_{j}")

    # 4. Area availability constraint
    for i in areas:
        model.addConstr(dispatch_plan.sum(i, '*') <= available_taxis[i], name=f"Availability_{i}")
    
    # Optimize the model
    model.optimize()

    # --- Return Results ---
    if model.status == GRB.OPTIMAL:
        return {"status": "optimal", "obj": model.objVal}
    else:
        return {"status": f"{model.status}"}


# Run the solver function
if __name__ == '__main__':
    result = solve_profitable_taxi_dispatch()
    print(result)