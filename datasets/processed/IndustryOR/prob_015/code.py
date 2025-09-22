from gurobipy import Model, GRB

# --- Model Initialization ---
model = Model("Procurement_and_Sales_Plan")

# --- Parameters ---
purchase_prices = [8, 6, 9]
sell_prices = [9, 8, 10]
months = range(3)  # 0-based index for months 1, 2, 3
initial_inventory = 200

# --- Decision Variables ---
# Purchase quantities
x = model.addVars(months, vtype=GRB.INTEGER, name="Purchase", lb=0) 
# Sales quantities
y = model.addVars(months, vtype=GRB.INTEGER, name="Sell", lb=0) 
# Inventory quantities
s = model.addVars(months, vtype=GRB.INTEGER, name="Inventory", lb=0)

# --- Constraints ---
for t in months:
    if t == 0:
        prev_inventory = initial_inventory
    else:
        prev_inventory = s[t - 1]

    # Inventory balance constraint
    model.addConstr(s[t] == prev_inventory + x[t] - y[t],
                    name=f"Inventory_Balance_{t+1}")

    # Inventory capacity constraints
    model.addConstr(s[t] <= 500, name=f"Inventory_Capacity_{t+1}")
    model.addConstr(prev_inventory + x[t] <= 500, name=f"Inventory_Capacity2_{t+1}")

    # Sales limit constraint
    model.addConstr(y[t] <= prev_inventory + x[t], name=f"Sales_Limit_{t+1}")

# --- Objective Function ---
profit = sum(
    (sell_prices[t] * y[t] - purchase_prices[t] * x[t]) for t in months)
model.setObjective(profit, GRB.MAXIMIZE)

# --- Model Optimization ---
model.optimize()

# --- Output Results ---
if model.status == GRB.OPTIMAL:
    print("\nOptimal solution found:")
    for t in months:
        print(
            f"Month {t+1}: "
            f"Purchased = {x[t].X:.0f}, Sold = {y[t].X:.0f}, Inventory = {s[t].X:.0f}"
        )
    print(f"\nTotal Profit = {model.objVal:.2f} yuan")
else:
    print("No optimal solution found.")
