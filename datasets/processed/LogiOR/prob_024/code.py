import gurobipy as gp
from gurobipy import GRB


def solve_platinum_trading(
    vault_capacity=500,
    initial_inventory=150,
    selling_price=[30000, 35000, 40000, 36000, 38000, 42000],
    purchase_price=[32000, 36000, 38000, 33000, 39000, 40000]):
    """
    Solves the platinum trading optimization problem.
    """
    # --- 1. Model Creation ---
    model = gp.Model("PlatinumTrading")

    # --- 2. Parameters & Sets ---
    quarter_num = len(selling_price)
    quarters = range(1, quarter_num + 1)

    # --- 3. Decision Variables ---
    selling_amount = model.addVars(quarters, lb=0, name="SellingAmount")
    purchase_amount = model.addVars(quarters, lb=0, name="PurchaseAmount")
    inventory = model.addVars(quarters,
                              lb=0,
                              ub=vault_capacity,
                              name="Inventory")

    # --- 4. Objective Function ---
    # Maximize total profit
    objective = gp.quicksum(selling_price[q - 1] * selling_amount[q] -
                            purchase_price[q - 1] * purchase_amount[q]
                            for q in quarters)
    model.setObjective(objective, GRB.MAXIMIZE)

    # --- 5. Constraints ---
    # Constraint 1: Initial inventory constraint
    model.addConstr(inventory[1] == initial_inventory + purchase_amount[1] -
                    selling_amount[1], "InitialInventory")

    # Constraint 2: Inventory balance constraint
    model.addConstrs(
        (inventory[q] == inventory[q - 1] + purchase_amount[q] -
         selling_amount[q] for q in range(2, quarter_num + 1)),
        "InventoryBalance")

    # Constraint 3: Selling amount must be less than or equal to inventory
    model.addConstr(selling_amount[1] <= initial_inventory,
                    "InitialInventoryLimit")
    model.addConstrs((selling_amount[q] <= inventory[q - 1]
                      for q in range(2, quarter_num + 1)), "InventoryLimit")

    # --- 6. Solve the Model ---
    model.optimize()

    # --- 7. Return Results ---
    if model.status == GRB.OPTIMAL:
        return {"status": "optimal", "obj": model.ObjVal}
    else:
        return {"status": f"{model.status}"}


# Run the solver function
if __name__ == "__main__":
    result = solve_platinum_trading()
    print(result)
