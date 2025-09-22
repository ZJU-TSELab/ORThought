import gurobipy as gp
from gurobipy import GRB

# Create a new model
model = gp.Model("Manufacturing_Plan")

# Decision variables
# x = number of microwave ovens to produce per month
# y = number of water heaters to produce per month
# oa = overtime hours in workshop A
x = model.addVar(lb=0, vtype=GRB.INTEGER, name="microwave_ovens")
y = model.addVar(lb=0, vtype=GRB.INTEGER, name="water_heaters")
oa = model.addVar(lb=0, ub=20, vtype=GRB.CONTINUOUS, name="overtime_A")
ob = model.addVar(lb=0, vtype=GRB.CONTINUOUS, name="overtime_B")

# Parameters
# Workshop hours required per product
hours_A_microwave = 2  # hours in workshop A per microwave
hours_B_microwave = 1  # hours in workshop B per microwave
hours_A_heater = 1  # hours in workshop A per water heater
hours_B_heater = 3  # hours in workshop B per water heater

# Workshop capacities
capacity_A = 250  # regular hours in workshop A
capacity_B = 150  # hours in workshop B

# Costs
cost_per_hour_A = 80  # yuan per hour in workshop A
cost_per_hour_B = 20  # yuan per hour in workshop B
inspection_sales_microwave = 30  # yuan per microwave
inspection_sales_heater = 50  # yuan per water heater

# Sales estimates
estimated_demand_microwave = 80  # microwave ovens per month
estimated_demand_heater = 50  # water heaters per month

# Constraints

# 1. Inspection and sales costs constraint
model.addConstr(
    inspection_sales_microwave * x + inspection_sales_heater * y <= 5500,
    "inspection_sales_cost")

# 2. Minimum microwave oven sales requirement
model.addConstr(x >= estimated_demand_microwave, "min_microwave_sales")

# 3a. Workshop A hours must be fully utilized (including potential overtime)
model.addConstr(hours_A_microwave * x + hours_A_heater * y == capacity_A + oa,
                "workshop_A_utilization")

# 3b. Workshop B hours must be fully utilized
model.addConstr(hours_B_microwave * x + hours_B_heater * y == capacity_B + ob,
                "workshop_B_utilization")

# 4. Overtime constraint for workshop A (Already handled in variable definition with ub=20)

# 5. Minimum water heater sales requirement
model.addConstr(y >= estimated_demand_heater, "min_heater_sales")

# Objective: Maximize profit
# Revenue isn't specified, so we'll minimize costs instead
total_cost = (
    # Production costs
    cost_per_hour_A * (capacity_A + oa) +  # Regular + overtime for workshop A
    cost_per_hour_B * (capacity_B + ob) +  # Regular hours for workshop B
    # Inspection and sales costs
    inspection_sales_microwave * x + inspection_sales_heater * y)

model.setObjective(total_cost, GRB.MINIMIZE)

# Solve the model
model.optimize()

# Check if a solution was found
if model.status == GRB.OPTIMAL:
    print("\n=== OPTIMAL MONTHLY PRODUCTION PLAN ===")
    print(f"Microwave Ovens: {int(x.X)} units")
    print(f"Water Heaters: {int(y.X)} units")
    print(f"Overtime Hours in Workshop A: {oa.X:.2f} hours")

    # Calculate resource utilization
    hours_used_A = hours_A_microwave * x.X + hours_A_heater * y.X
    hours_used_B = hours_B_microwave * x.X + hours_B_heater * y.X

    print("\n=== RESOURCE UTILIZATION ===")
    print(
        f"Workshop A: {hours_used_A:.2f} hours used (including {oa.X:.2f} overtime hours)"
    )
    print(f"Workshop B: {hours_used_B:.2f} hours used (out of {capacity_B})")

    # Calculate costs
    production_cost_A = cost_per_hour_A * hours_used_A
    production_cost_B = cost_per_hour_B * hours_used_B
    inspection_sales_cost = inspection_sales_microwave * x.X + inspection_sales_heater * y.X

    print("\n=== COST BREAKDOWN ===")
    print(f"Workshop A Production Cost: {production_cost_A:.2f} yuan")
    print(f"Workshop B Production Cost: {production_cost_B:.2f} yuan")
    print(f"Inspection and Sales Cost: {inspection_sales_cost:.2f} yuan")
    print(f"Total Cost: {model.objVal:.2f} yuan")

    # Check constraint satisfaction
    print("\n=== CONSTRAINT VERIFICATION ===")
    print(
        f"1. Inspection and Sales Cost: {inspection_sales_cost:.2f} yuan (Max: 5500 yuan)"
    )
    print(
        f"2. Microwave Oven Production: {int(x.X)} units (Min: {estimated_demand_microwave} units)"
    )
    print(
        f"3. Workshop A Utilization: {hours_used_A:.2f} hours (Regular: {capacity_A} hours, Overtime: {oa.X:.2f} hours)"
    )
    print(
        f"   Workshop B Utilization: {hours_used_B:.2f} hours (Capacity: {capacity_B} hours)"
    )
    print(f"4. Workshop A Overtime: {oa.X:.2f} hours (Max: 20 hours)")
    print(
        f"5. Water Heater Production: {int(y.X)} units (Min: {estimated_demand_heater} units)"
    )

    # Check for binding constraints
    print("\n=== BINDING CONSTRAINTS ===")
    for c in model.getConstrs():
        if abs(c.slack) < 1e-6:
            print(f"- {c.ConstrName} is binding")

elif model.status == GRB.INFEASIBLE:
    print(
        "The model is infeasible - there is no solution that satisfies all constraints."
    )
    # Compute and display the Irreducible Inconsistent Subsystem (IIS)
    print("Computing IIS to find conflicting constraints...")
    model.computeIIS()
    print("\nThe following constraints are in conflict:")
    for c in model.getConstrs():
        if c.IISConstr:
            print(f"- {c.ConstrName}")
else:
    print(
        f"Optimization did not complete normally. Status code: {model.status}")
