import gurobipy as gp
from gurobipy import GRB


def solve_greentech_manufacturing(
    cost_per_ton_method={"Method1": 4.20, "Method2": 3.80, "Method3": 4.50},
    yield_per_method={
        "Method1": {"Q6": 0.3, "Q8": 0.4, "Q10": 0.3},
        "Method2": {"Q6": 0.5, "Q8": 0.3, "Q10": 0.2},
        "Method3": {"Q6": 0.2, "Q8": 0.5, "Q10": 0.3}
    },
    actual_quality_values={"Q6": 6, "Q8": 8, "Q10": 10},
    upgrade_cost={"Q6_to_Q8": 1.20, "Q8_to_Q10": 1.80},
    price_per_ton={"Premium": 15, "Standard": 8},
    min_quality_score_req={"Premium": 9, "Standard": 7},
    max_demand={"Premium": 2500, "Standard": 800}
):
    """
    Models and solves the GreenTech Manufacturing problem.
    """
    # Create a new model
    model = gp.Model("GreenTechManufacturing")

    # --- Sets ---
    packaging_types = ["Premium", "Standard"]
    methods = ["Method1", "Method2", "Method3"]
    quality_labels = ["Q6", "Q8", "Q10"]

    # --- Decision Variables ---
    processing_amount = model.addVars(methods, name="ProcessingAmount", lb=0)
    quality6_upgrade_amount = model.addVar(name="Quality6UpgradeAmount", lb=0)
    quality8_upgrade_amount = model.addVar(name="Quality8UpgradeAmount", lb=0)
    packaging_produced = model.addVars(packaging_types, quality_labels, name="PackagingProduced", lb=0)

    # --- Objective Function: Maximize Total Profit ---
    total_revenue = gp.quicksum(price_per_ton[p] * packaging_produced.sum(p, '*') for p in packaging_types)
    total_processing_cost = gp.quicksum(cost_per_ton_method[m] * processing_amount[m] for m in methods)
    total_upgrade_cost = (upgrade_cost["Q6_to_Q8"] * quality6_upgrade_amount +
                          upgrade_cost["Q8_to_Q10"] * quality8_upgrade_amount)
    model.setObjective(total_revenue - total_processing_cost - total_upgrade_cost, GRB.MAXIMIZE)

    # --- Constraints ---
    for p in packaging_types:
        weighted_quality_sum = gp.quicksum(actual_quality_values[q_label] * packaging_produced[p, q_label]
                                           for q_label in quality_labels)
        total_produced_p = packaging_produced.sum(p, '*')
        model.addConstr(weighted_quality_sum >= min_quality_score_req[p] * total_produced_p,
                        name=f"QualityScore_{p}")

    for p in packaging_types:
        model.addConstr(packaging_produced.sum(p, '*') <= max_demand[p], name=f"Demand_{p}")

    produced_q6_material = gp.quicksum(yield_per_method[m]["Q6"] * processing_amount[m] for m in methods)
    used_as_q6_in_packaging = gp.quicksum(packaging_produced[p, "Q6"] for p in packaging_types)
    model.addConstr(produced_q6_material - quality6_upgrade_amount >= used_as_q6_in_packaging, name="Balance_Q6")

    produced_q8_material_native = gp.quicksum(yield_per_method[m]["Q8"] * processing_amount[m] for m in methods)
    total_available_q8_material = produced_q8_material_native + quality6_upgrade_amount
    used_as_q8_in_packaging = gp.quicksum(packaging_produced[p, "Q8"] for p in packaging_types)
    model.addConstr(total_available_q8_material - quality8_upgrade_amount >= used_as_q8_in_packaging, name="Balance_Q8")

    produced_q10_material_native = gp.quicksum(yield_per_method[m]["Q10"] * processing_amount[m] for m in methods)
    total_available_q10_material = produced_q10_material_native + quality8_upgrade_amount
    used_as_q10_in_packaging = gp.quicksum(packaging_produced[p, "Q10"] for p in packaging_types)
    model.addConstr(total_available_q10_material >= used_as_q10_in_packaging, name="Balance_Q10")

    # Optimize the model
    model.optimize()

    # Return Results
    if model.status == GRB.OPTIMAL:
        return {"status": "optimal", "obj": model.ObjVal}
    else:
        return {"status": f"{model.status}"}


if __name__ == '__main__':
    result = solve_greentech_manufacturing()
    print(result)
