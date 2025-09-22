import gurobipy as gp
from gurobipy import GRB


def solve_pricing_optimization(
    priority_service_value=[120, 90],
    economy_service_value=[80, 110],
    small_business_potential=1000,
    large_enterprise_potential=1500
):
    """
    Models and solves the pricing optimization problem.
    """
    # Create a new model
    model = gp.Model("pricing_optimization")

    # Decision Variables
    priority_price = model.addVar(name="PriorityPrice", lb=0, ub=priority_service_value[0])
    economy_price = model.addVar(name="EconomyPrice", lb=0, ub=economy_service_value[1])

    # Objective: Maximize total revenue
    model.setObjective(
        small_business_potential * priority_price + large_enterprise_potential * economy_price,
        GRB.MAXIMIZE
    )

    # Constraint 1: Small business chooses Priority
    model.addConstr(
        priority_service_value[0] - priority_price >= economy_service_value[0] - economy_price,
        "small_business_preference"
    )

    # Constraint 2: Large enterprise chooses Economy
    model.addConstr(
        priority_service_value[1] - priority_price <= economy_service_value[1] - economy_price,
        "large_enterprise_preference"
    )

    # Constraint 3: Price of Priority service must be at least $15 higher than Economy service
    model.addConstr(
        priority_price - economy_price >= 15,
        "price_difference"
    )

    # Solve the model
    model.optimize()

    # Return Results
    if model.status == GRB.OPTIMAL:
        return {"status": "optimal", "obj": model.ObjVal}
    else:
        return {"status": f"{model.status}"}


if __name__ == "__main__":
    result = solve_pricing_optimization()
    print(result)
