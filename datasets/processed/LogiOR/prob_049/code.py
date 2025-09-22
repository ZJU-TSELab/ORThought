import gurobipy as gp
from gurobipy import GRB


def solve_logistics_optimization(
    distance_packaging_loading=1400.0,
    daily_trips=[
        [0, 20, 15, 10],
        [20, 0, 25, 30],
        [15, 25, 0, 40],
        [10, 30, 40, 0]
    ],
    cost_per_meter_per_trip=0.50,
    minimal_distance=100.0
):
    """
    Solves the logistics optimization problem.
    """
    try:
        # --- Create a new model ---
        model = gp.Model("LogisticsOptimization")

        # --- Decision Variables ---
        d_S_St = model.addVar(lb=minimal_distance, name="DistanceBetweenSortingAndStorage")
        d_S_Pk = model.addVar(lb=minimal_distance, name="DistanceBetweenSortingAndPackaging")
        d_S_L = model.addVar(lb=minimal_distance, name="DistanceBetweenSortingAndLoading")
        d_St_Pk = model.addVar(lb=minimal_distance, name="DistanceBetweenStorageAndPackaging")
        d_St_L = model.addVar(lb=minimal_distance, name="DistanceBetweenStorageAndLoading")

        # --- Objective Function ---
        cost_Pk_L = (daily_trips[0][1] + daily_trips[1][0]) * distance_packaging_loading
        cost_Pk_S = (daily_trips[0][2] + daily_trips[2][0]) * d_S_Pk
        cost_Pk_St = (daily_trips[0][3] + daily_trips[3][0]) * d_St_Pk
        cost_L_S = (daily_trips[1][2] + daily_trips[2][1]) * d_S_L
        cost_L_St = (daily_trips[1][3] + daily_trips[3][1]) * d_St_L
        cost_S_St = (daily_trips[2][3] + daily_trips[3][2]) * d_S_St
        total_transport_cost_before_factor = cost_Pk_L + cost_Pk_S + cost_Pk_St + cost_L_S + cost_L_St + cost_S_St
        model.setObjective(total_transport_cost_before_factor * cost_per_meter_per_trip, GRB.MINIMIZE)

        # --- Constraints ---
        model.addConstr(d_S_L + d_S_Pk == distance_packaging_loading, "Collinearity_Sorting")
        model.addConstr(d_St_Pk + d_St_L == distance_packaging_loading, "Collinearity_Storage")
        model.addConstr(d_S_St <= distance_packaging_loading, "MaxDist_SortingStorage")

        # --- Optimize model ---
        model.optimize()

        # --- Return solution ---
        if model.status == GRB.OPTIMAL:
            return {"status": "optimal", "obj": model.ObjVal}
        else:
            return {"status": f"{model.status}"}

    except gp.GurobiError as e:
        return {"status": f"Gurobi error: {e}"}
    except Exception as e:
        return {"status": f"An unexpected error occurred: {e}"}


if __name__ == "__main__":
    result = solve_logistics_optimization()
    print(result)
