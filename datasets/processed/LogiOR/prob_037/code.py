import gurobipy as gp
from gurobipy import GRB

def solve(
    I=[1, 2],
    p=[2, 3],
    h_r=2,
    h_q=[3, 4],
    p_q=[1, 1],
    c_q=[5, 6],
    s=[10, 12],
    s_q=[20, 25],
    c_r=5,
    H_max=8000,
    R_max=3000
):
    """
    Args:
        I: Category identifiers.
        p: Units of base product produced per unit of raw material for each category.
        h_r: Labor hours required per unit of raw material processed.
        h_q: Labor hours required per unit of premium product processed for each category.
        p_q: Base-to-premium conversion coefficient for each category (base units consumed per 1 premium).
        c_q: Additional processing cost per unit of premium product for each category.
        s: Selling price per unit of base product for each category.
        s_q: Selling price per unit of premium product for each category.
        c_r: Raw material cost per unit.
        H_max: Total available labor hours.
        R_max: Maximum purchasable raw material units.
    """
    
    # Create a new model
    model = gp.Model("Product Manufacturing Optimization")
    
    # Sets
    N = range(len(I))  # Categories
    
    # Decision Variables
    r = model.addVar(vtype=GRB.INTEGER, lb=0, name="raw_material_purchased")
    x = model.addVars(N, vtype=GRB.INTEGER, lb=0, name="product_produced_wo_further_processing")
    y = model.addVars(N, vtype=GRB.INTEGER, lb=0, name="premium_product_produced")
    
    # Objective
    revenue = gp.quicksum(s[i] * x[i] for i in N) + gp.quicksum(s_q[i] * y[i] for i in N)
    raw_material_cost = c_r * r
    processing_cost = gp.quicksum(c_q[i] * y[i] for i in N)
    model.setObjective(revenue - raw_material_cost - processing_cost, GRB.MAXIMIZE)
    
    # Constraints
    # Constraint 1: Labor hours constraint
    labor_hours = h_r * r + gp.quicksum(h_q[i] * y[i] for i in N)
    model.addConstr(labor_hours <= H_max, "LaborHoursLimit")
    
    # Constraint 2: Raw material constraint
    model.addConstr(r <= R_max, "RawMaterialLimit")
    
    # Constraint 3: Material balance constraint
    for i in N:
        model.addConstr(
            x[i] + p_q[i] * y[i] == p[i] * r,
            f"MaterialBalance_{i}",
        )
    
    # Optimize the model
    model.optimize()
    
    # Return Results
    if model.status == GRB.OPTIMAL:
        return {"status": "optimal", "obj": model.ObjVal}
    else:
        return {"status": f"{model.status}"}
    
if __name__ == "__main__":
    result = solve()
    print(result)
