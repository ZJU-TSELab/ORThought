import gurobipy as gp
from gurobipy import GRB


def solve_drone_tsp(
    flight_times_input=[
        [0, 8, 12, 15, 7, 10, 14],
        [8, 0, 5, 11, 6, 9, 13],
        [12, 5, 0, 7, 10, 4, 8],
        [15, 11, 7, 0, 9, 6, 5],
        [7, 6, 10, 9, 0, 3, 11],
        [10, 9, 4, 6, 3, 0, 7],
        [14, 13, 8, 5, 11, 7, 0]
    ]
):
    """
    Solves the Drone Traveling Salesperson Problem (TSP).
    """
    try:
        # --- Parameters ---
        customer_locations_set = {"C1", "C2", "C3", "C4", "C5", "C6"}
        depot_name = "Depot"
        location_names = [depot_name] + sorted(list(customer_locations_set))
        num_total_locations = len(location_names)
        depot_index = 0
        customer_indices = list(range(1, num_total_locations))

        flight_time_matrix = {
            (i, j): flight_times_input[i][j]
            for i in range(num_total_locations)
            for j in range(num_total_locations)
        }

        # --- Create a new model ---
        model = gp.Model("DroneTSP")

        # --- Decision Variables ---
        arcs = [(i, j) for i in range(num_total_locations) for j in range(num_total_locations) if i != j]
        x = model.addVars(arcs, vtype=GRB.BINARY, name="Route")

        # --- Objective Function ---
        model.setObjective(gp.quicksum(flight_time_matrix[i, j] * x[i, j] for i, j in arcs), GRB.MINIMIZE)

        # --- Constraints ---
        model.addConstr(gp.quicksum(x[depot_index, j] for j in customer_indices) == 1, "LeaveDepot")
        model.addConstr(gp.quicksum(x[i, depot_index] for i in customer_indices) == 1, "ReturnToDepot")

        for j in customer_indices:
            model.addConstr(gp.quicksum(x[i, j] for i in range(num_total_locations) if i != j) == 1, f"EnterCustomer_{j}")

        for i in customer_indices:
            model.addConstr(gp.quicksum(x[i, j] for j in range(num_total_locations) if i != j) == 1, f"LeaveCustomer_{i}")

        num_customers = len(customer_indices)
        u = model.addVars(customer_indices, lb=1.0, ub=float(num_customers), vtype=GRB.CONTINUOUS, name="u")

        for i in customer_indices:
            for j in customer_indices:
                if i != j:
                    model.addConstr(u[i] - u[j] + num_customers * x[i, j] <= num_customers - 1, f"MTZ_{i}_{j}")

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
    result = solve_drone_tsp()
    print(result)
