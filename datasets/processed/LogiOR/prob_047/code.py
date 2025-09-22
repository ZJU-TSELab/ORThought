import gurobipy as gp
from gurobipy import GRB


def solve_warehouse_scheduling(
    orders_received={'midnight_6am': 150, '6am_noon': 250, 'noon_6pm': 400, '6pm_midnight': 300},
    hourly_wage=12,
    shift_hours=6,
    orders_per_worker=60,
    penalty_per_unprocessed_order=1
):
    """
    Models and solves the warehouse scheduling problem.
    """
    model = gp.Model("WarehouseScheduling")
    model.setParam('OutputFlag', 0)

    # --- Parameters ---
    shifts = ['midnight_6am', '6am_noon', 'noon_6pm', '6pm_midnight']
    shift_wage = hourly_wage * shift_hours

    # --- Decision Variables ---
    workers = model.addVars(shifts, name="Workers", vtype=GRB.INTEGER, lb=0)
    orders_processed = model.addVars(shifts, name="OrdersProcessed", vtype=GRB.CONTINUOUS, lb=0)
    unprocessed = model.addVars(shifts, name="UnprocessedOrders", vtype=GRB.CONTINUOUS, lb=0)

    # --- Objective Function ---
    total_cost = gp.LinExpr()
    for shift in shifts:
        total_cost += workers[shift] * shift_wage
        total_cost += unprocessed[shift] * penalty_per_unprocessed_order
    model.setObjective(total_cost, GRB.MINIMIZE)

    # --- Constraints ---
    for shift in shifts:
        model.addConstr(orders_processed[shift] <= workers[shift] * orders_per_worker,
                        name=f"ProcessingCapacity_{shift}")

    shift_order = ['midnight_6am', '6am_noon', 'noon_6pm', '6pm_midnight']
    for i, shift in enumerate(shift_order):
        if shift == 'midnight_6am':
            model.addConstr(orders_processed[shift] + unprocessed[shift] == orders_received[shift],
                           name=f"OrderBalance_{shift}")
        else:
            prev_shift = shift_order[i-1]
            model.addConstr(orders_processed[shift] + unprocessed[shift] ==
                           orders_received[shift] + unprocessed[prev_shift],
                           name=f"OrderBalance_{shift}")

    model.addConstr(unprocessed['6pm_midnight'] == 0, name="AllOrdersProcessedByMidnight")

    # --- Solve ---
    model.optimize()

    # --- Return Results ---
    if model.status == GRB.OPTIMAL:
        return {"status": "optimal", "obj": model.ObjVal}
    else:
        return {"status": f"{model.status}"}


if __name__ == '__main__':
    result = solve_warehouse_scheduling()
    print(result)