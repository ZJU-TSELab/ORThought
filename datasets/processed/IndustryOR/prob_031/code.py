from gurobipy import Model, GRB

# Data from Table 1.4
workshops = ['A', 'B', 'C', 'D']
components = [1, 2, 3]

# Production capacity (in hours) for each workshop
prod_capacity = {'A': 100, 'B': 150, 'C': 80, 'D': 200}

# Production rate (units/hour) for each component in each workshop
prod_rate = {
    ('A', 1): 10,
    ('A', 2): 15,
    ('A', 3): 5,
    ('B', 1): 15,
    ('B', 2): 10,
    ('B', 3): 5,
    ('C', 1): 20,
    ('C', 2): 5,
    ('C', 3): 10,
    ('D', 1): 10,
    ('D', 2): 15,
    ('D', 3): 20
}

# Create model
model = Model("Maximize_Complete_Products")

# Add variables
x = model.addVars(workshops, components, lb=0, name="x")  # Hours allocated
z = model.addVar(name="z", vtype=GRB.INTEGER)  # Number of complete products

# Set objective: maximize z
model.setObjective(z, GRB.MAXIMIZE)

# Add constraints:

# 1. For each component, total produced >= z
for j in components:
    model.addConstr(sum(prod_rate[i, j] * x[i, j] for i in workshops) >= z,
                    name=f"Component_{j}_enough_for_z")

# 2. Workshop time availability constraint
for i in workshops:
    model.addConstr(sum(x[i, j] for j in components) <= prod_capacity[i],
                    name=f"Workshop_{i}_time_limit")

# Optimize
model.optimize()

# Output results
if model.status == GRB.OPTIMAL:
    print(f"\nMaximum number of complete products: {z.X:.2f}\n")

    print("Hours allocated per component:")
    for i in workshops:
        for j in components:
            if x[i, j].X > 0:
                print(f"Workshop {i}, Component {j}: {x[i, j].X:.2f} hours")
else:
    print("No optimal solution found.")
