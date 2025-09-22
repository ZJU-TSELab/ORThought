import gurobipy as gp
from gurobipy import GRB

# Create a new model
model = gp.Model("Carelland_GDP_Maximization")

# Define the commodities
commodities = ["steel", "engines", "electronics", "plastic"]

# Unit prices in local currency (Klunz)
unit_price = {
    "steel": 500,
    "engines": 1500,
    "electronics": 300,
    "plastic": 1200
}

# Input requirements matrix:
# input_requirements[output][input] = amount of input needed to produce 1 unit of output
input_requirements = {
    "steel": {
        "engines": 0.02,
        "plastic": 0.01,
        "steel": 0,
        "electronics": 0
    },
    "engines": {
        "steel": 0.8,
        "electronics": 0.15,
        "plastic": 0.11,
        "engines": 0
    },
    "electronics": {
        "steel": 0.01,
        "engines": 0.01,
        "plastic": 0.05,
        "electronics": 0
    },
    "plastic": {
        "steel": 0.2,
        "engines": 0.03,
        "electronics": 0.05,
        "plastic": 0
    }
}

# Additional imported goods required (in Klunz)
imported_goods = {
    "steel": 250,
    "engines": 300,
    "electronics": 50,
    "plastic": 300
}

# Labor requirements (in person-months)
labor_requirements = {
    "steel": 6,  # 6 person-months
    "engines": 12,  # 1 person-year = 12 person-months
    "electronics": 6,  # 6 person-months
    "plastic": 24  # 2 person-years = 24 person-months
}

# Production limits
production_limits = {"engines": 650000, "plastic": 60000}

# Total available labor force (in person-months)
total_labor = 830000

# Decision variables: quantity of each commodity to produce
x = {}
for commodity in commodities:
    x[commodity] = model.addVar(vtype=GRB.CONTINUOUS,
                                name=f"produce_{commodity}")

# Net export variables (production minus domestic consumption)
net_export = {}
for commodity in commodities:
    net_export[commodity] = model.addVar(vtype=GRB.CONTINUOUS,
                                         name=f"net_export_{commodity}")

# Add constraints
# 1. Commodity balance constraints
for commodity in commodities:
    # Net export = production - domestic consumption
    model.addConstr(
        net_export[commodity] == x[commodity] -
        gp.quicksum(input_requirements[other][commodity] * x[other]
                    for other in commodities), f"balance_{commodity}")

# 2. Production limit constraints
for commodity, limit in production_limits.items():
    model.addConstr(x[commodity] <= limit, f"limit_{commodity}")

# 3. Labor constraint
model.addConstr(
    gp.quicksum(labor_requirements[commodity] * x[commodity]
                for commodity in commodities) <= total_labor,
    "labor_constraint")

# 4. Non-negativity constraint for net exports (assuming we can't import these commodities)
for commodity in commodities:
    model.addConstr(net_export[commodity] >= 0,
                    f"non_negative_export_{commodity}")

# Objective function: Maximize GDP (value of production minus cost of imported goods)
gdp = gp.quicksum(unit_price[commodity] * net_export[commodity]
                  for commodity in commodities) - gp.quicksum(
                      imported_goods[commodity] * x[commodity]
                      for commodity in commodities)

model.setObjective(gdp, GRB.MAXIMIZE)

# Optimize the model
model.optimize()

# Print the results
print("\n=== OPTIMAL SOLUTION ===")
if model.status == GRB.OPTIMAL:
    print("\nProduction Quantities:")
    for commodity in commodities:
        print(f"{commodity.capitalize()}: {x[commodity].X:.2f} units")

    print("\nNet Exports:")
    for commodity in commodities:
        print(f"{commodity.capitalize()}: {net_export[commodity].X:.2f} units")

    print("\nCost of Imported Goods:")
    total_import_cost = sum(imported_goods[commodity] * x[commodity].X
                            for commodity in commodities)
    print(f"Total: {total_import_cost:.2f} Klunz")

    print("\nValue of Exported Goods:")
    total_export_value = sum(unit_price[commodity] * net_export[commodity].X
                             for commodity in commodities)
    print(f"Total: {total_export_value:.2f} Klunz")

    print(f"\nMaximum GDP: {model.ObjVal:.2f} Klunz")

    # Calculate and print resource utilization
    labor_used = sum(labor_requirements[commodity] * x[commodity].X
                     for commodity in commodities)
    print(
        f"\nLabor Used: {labor_used:.2f} person-months (out of {total_labor})")

    for commodity, limit in production_limits.items():
        utilization = (x[commodity].X / limit) * 100 if limit > 0 else 0
        print(
            f"{commodity.capitalize()} Production Capacity Used: {utilization:.2f}%"
        )
else:
    print(f"Optimization failed. Status code: {model.status}")
