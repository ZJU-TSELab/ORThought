import gurobipy as gp
from gurobipy import GRB
from typing import Dict

def solve_delivery_optimization(
    TotalOrdersAvailable: int = 1500,
    OrdersPerRider: int = 12,
    RevenuePerOrder: float = 15.0,
    MinOrdersRequired: int = 1000,
    MinBaseFee: float = 3.0,
    RiderModelCoeffs: Dict[str, float] = {'base_fee_sq': 0.8, 'bonus': 17.0}
):
    """
    Solves the food delivery platform's compensation optimization problem.

    Args:
        TotalOrdersAvailable (int): Total orders needing delivery.
        OrdersPerRider (int): Average orders a rider can complete.
        RevenuePerOrder (float): Revenue earned per completed order.
        MinOrdersRequired (int): Minimum number of orders that must be completed.
        MinBaseFee (float): Minimum allowed base delivery fee.
        RiderModelCoeffs (Dict[str, float]): Coefficients for the rider availability model.
    """
    
    # --- Model Initialization ---
    model = gp.Model("DeliveryPlatformOptimization")

    # --- Decision Variables ---
    # base_fee (b): The base delivery fee per order.
    base_fee = model.addVar(name="BaseFee", vtype=GRB.CONTINUOUS, lb=MinBaseFee)
    
    # bonus (p): The additional bonus per order.
    bonus = model.addVar(name="Bonus", vtype=GRB.CONTINUOUS, lb=0.0)
    
    # orders_completed (c): The total number of orders completed.
    orders_completed = model.addVar(
        name="OrdersCompleted", 
        vtype=GRB.INTEGER, 
        lb=MinOrdersRequired, 
        ub=TotalOrdersAvailable
    )

    # --- Objective Function ---
    # Maximize: Total Revenue - Total Rider Payout
    # Maximize: c * RevenuePerOrder - c * (base_fee + bonus)
    total_profit = orders_completed * (RevenuePerOrder - base_fee - bonus)
    model.setObjective(total_profit, GRB.MAXIMIZE)

    # --- Constraints ---
    # Rider Capacity Constraint:
    # Completed orders <= Total rider capacity
    # Rider capacity = (Number of riders) * (Orders per rider)
    # Number of riders = 0.8 * b^2 + 15 * p
    num_riders = RiderModelCoeffs['base_fee_sq'] * base_fee * base_fee + RiderModelCoeffs['bonus'] * bonus
    rider_capacity = num_riders * OrdersPerRider
    model.addConstr(orders_completed <= rider_capacity, "RiderCapacity")

    # --- Solver Configuration ---
    # This is a non-convex quadratic problem (objective and constraint).
    # We must set the 'NonConvex' parameter to 2 for Gurobi to solve it.
    model.setParam('NonConvex', 2)

    # --- Solve the Model ---
    model.optimize()

    # --- Return Results ---
    if model.Status == GRB.OPTIMAL:
        return {"status": "optimal", "obj": model.ObjVal}
    else:
        return {"status": f"{model.Status}"}


if __name__ == "__main__":
    # Call the function with the problem's default parameters.
    result = solve_delivery_optimization()
    print(result)
