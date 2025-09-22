import gurobipy as gp
from gurobipy import GRB


def solve_shipping_minlp_robust(
    vessels=["Ship_A", "Ship_B", "Ship_C"],
    distance=6000.0,
    max_time=288.0,
    fuel_price=4000.0,
    carbon_tax=300.0,
    max_speed=30.0,
    fixed_cost={
        "Ship_A": 500000,
        "Ship_B": 600000,
        "Ship_C": 450000
    },
    co2_factor={
        "Ship_A": 3.2,
        "Ship_B": 3.15,
        "Ship_C": 3.25
    },
    fuel_coeffs={
        "Ship_A": {"a": 0.005, "b": 0.1, "c": 1.2},
        "Ship_B": {"a": 0.004, "b": 0.08, "c": 1.5},
        "Ship_C": {"a": 0.006, "b": 0.12, "c": 1.0}
    }
):
    """
    Solves the vessel selection and speed optimization problem using a robust
    MIQCP (Mixed-Integer Quadratically Constrained Programming) formulation.
    """
    # Create a new model
    model = gp.Model("ShippingOptimization_Robust")

    # --- Decision Variables ---
    # 1. Binary variable to select exactly one vessel
    select_vessel = model.addVars(vessels, vtype=GRB.BINARY, name="SelectVessel")

    # 2. Continuous variable for the speed of EACH vessel
    speed_per_vessel = model.addVars(vessels, lb=0.0, ub=max_speed, name="Speed")

    # 3. Auxiliary variable z_s = y_s / v_s
    aux_z = model.addVars(vessels, lb=0.0, name="Aux_Z")

    # --- Constraints ---
    # 1. Vessel Selection Constraint: Exactly one vessel must be chosen
    model.addConstr(select_vessel.sum('*') == 1, name="OneVesselMustBeSelected")

    # 2. Link speed to vessel selection
    min_speed = distance / max_time
    for s in vessels:
        # The speed v_s must be >= min_speed if vessel s is selected (y_s=1)
        model.addConstr(speed_per_vessel[s] >= min_speed * select_vessel[s], name=f"MinSpeed_{s}")
        # The speed v_s must be <= max_speed if vessel s is selected (y_s=1)
        model.addConstr(speed_per_vessel[s] <= max_speed * select_vessel[s], name=f"MaxSpeed_{s}")

        # 3. Core non-convex quadratic constraint: z_s * v_s = y_s
        model.addQConstr(aux_z[s] * speed_per_vessel[s] == select_vessel[s], name=f"AuxConstraint_{s}")

    # --- Objective Function: Minimize Total Cost ---
    # Total Fixed Cost
    total_fixed_cost = select_vessel.prod(fixed_cost)

    # Total Variable Cost (Fuel + Carbon)
    # The original variable cost per ship was C_var * D * (a*v + b + c/v)
    # With our auxiliary variables, this becomes:
    # C_var * D * (a*v_s + b*y_s + c*z_s)
    total_variable_cost = gp.quicksum(
        (fuel_price + carbon_tax * co2_factor[s]) * distance * (
            fuel_coeffs[s]['a'] * speed_per_vessel[s] +
            fuel_coeffs[s]['b'] * select_vessel[s] +
            fuel_coeffs[s]['c'] * aux_z[s]
        ) for s in vessels
    )

    model.setObjective(total_fixed_cost + total_variable_cost, GRB.MINIMIZE)

    # --- Gurobi Settings for Non-Convex Problems ---
    model.Params.NonConvex = 2

    # Optimize the model
    model.optimize()

    # --- Return Results ---
    if model.status == GRB.OPTIMAL:
        return {"status": "optimal", "obj": model.objVal}
    else:
        return {"status": f"{model.status}"}


# Run the solver function
if __name__ == '__main__':
    result = solve_shipping_minlp_robust()
    print(result)