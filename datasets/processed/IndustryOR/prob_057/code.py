from gurobipy import Model, GRB, quicksum

# Create a new model
model = Model("Farm_Optimization")

# Define parameters
M = 120  # Maximum possible acres

# Decision variables: Acres planted
x_A = model.addVar(name="Acres_Apples", lb=0)
x_P = model.addVar(name="Acres_Pears", lb=0)
x_O = model.addVar(name="Acres_Oranges", lb=0)
x_L = model.addVar(name="Acres_Lemons", lb=0)

# Binary variables: Whether to plant a certain type of fruit    
y_A = model.addVar(vtype=GRB.BINARY, name="Use_Apples")
y_P = model.addVar(vtype=GRB.BINARY, name="Use_Pears")
y_O = model.addVar(vtype=GRB.BINARY, name="Use_Oranges")
y_L = model.addVar(vtype=GRB.BINARY, name="Use_Lemons")

# Set objective function
model.setObjective(2000 * x_A + 1800 * x_P + 2200 * x_O + 3000 * x_L,
                   GRB.MAXIMIZE)

# Add constraints
model.addConstr(x_A + x_P + x_O + x_L <= 120, "Total_Area_Constraint")  # Total area constraint
model.addConstr(x_A >= 2 * x_P, "Apples_vs_Pears")  # Apples ≥ 2×Pears
model.addConstr(x_A >= 3 * x_L, "Apples_vs_Lemons")  # Apples ≥ 3×Lemons
model.addConstr(x_O == 2 * x_L, "Oranges_vs_Lemons")  # Oranges = 2×Lemons
model.addConstr(y_A + y_P + y_O + y_L <= 2, "Max_Two_Crops")  # At most two types of fruits

# Big-M constraints: Link area planted to whether a fruit is planted    
model.addConstr(x_A <= M * y_A, "Link_Apples")
model.addConstr(x_P <= M * y_P, "Link_Pears")
model.addConstr(x_O <= M * y_O, "Link_Oranges")
model.addConstr(x_L <= M * y_L, "Link_Lemons")

# Solve the model
model.optimize()

# Output results
if model.status == GRB.OPTIMAL:
    print("Optimal solution found!")
    print(f"Apples: {x_A.X:.2f} acres")
    print(f"Pears: {x_P.X:.2f} acres")
    print(f"Oranges: {x_O.X:.2f} acres")
    print(f"Lemons: {x_L.X:.2f} acres")
    print(f"Total profit: ${model.objVal:,.2f}")
else:
    print("No optimal solution found.")
