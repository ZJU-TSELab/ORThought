import gurobipy as gp
from gurobipy import GRB

def solve_green_freight_minlp(
    old_trucks=['D1', 'D2', 'D3', 'D4', 'D5'],
    annual_op_cost_old={
        'D1': 80000, 'D2': 85000, 'D3': 78000, 'D4': 92000, 'D5': 88000
    },
    annual_emissions_old={
        'D1': 15, 'D2': 16, 'D3': 14, 'D4': 18, 'D5': 17
    },
    annual_op_cost_new=30000,
    annualized_investment_new=120000,
    carbon_tax_coeff=80,
    min_fleet_size=4,
    max_new_trucks=3
):
    """
    Solves the Green Freight vehicle replacement problem to minimize total annual cost.
    This is a Mixed-Integer Non-Linear Programming (MINLP) problem due to the
    quadratic term in the carbon tax calculation.
    """
    # Create a new model
    model = gp.Model("GreenFreight")

    # --- Decision Variables ---
    # Binary variable: 1 if an old truck is kept, 0 if retired
    keep_old_truck = model.addVars(old_trucks, vtype=GRB.BINARY, name="KeepOldTruck")

    # Integer variable: number of new electric trucks to buy
    buy_new_trucks = model.addVar(vtype=GRB.INTEGER, name="BuyNewTrucks", lb=0)

    # --- Objective Function: Minimize Total Annual Cost ---
    
    # 1. Cost of operating the old trucks that are kept
    cost_kept_trucks = gp.quicksum(annual_op_cost_old[d] * keep_old_truck[d] 
                                   for d in old_trucks)

    # 2. Cost (operating + investment) of new trucks
    cost_new_trucks = (annual_op_cost_new + annualized_investment_new) * buy_new_trucks

    # 3. Punitive carbon tax (non-linear part)
    total_emissions = gp.quicksum(annual_emissions_old[d] * keep_old_truck[d] 
                                  for d in old_trucks)
    carbon_tax = carbon_tax_coeff * total_emissions * total_emissions

    model.setObjective(
        cost_kept_trucks + cost_new_trucks + carbon_tax,
        GRB.MINIMIZE
    )

    # --- Constraints ---
    
    # 1. Minimum fleet size constraint
    model.addConstr(keep_old_truck.sum('*') + buy_new_trucks >= min_fleet_size, 
                    name="MinFleetSize")

    # 2. New truck purchase limit
    model.addConstr(buy_new_trucks <= max_new_trucks, 
                    name="MaxNewTrucks")

    # The domain of the variables (Binary, Integer, >=0) is already set during their creation.

    # Optimize the model
    model.optimize()

    # --- Return Results ---
    if model.status == GRB.OPTIMAL:
        return {"status": "optimal", "obj": model.objVal}
    else:
        return {"status": f"{model.status}"}


# Run the solver function
if __name__ == '__main__':
    result = solve_green_freight_minlp()
    print(result)