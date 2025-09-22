import gurobipy as gp
from gurobipy import GRB

def optimize_production():
    # Create a new model
    model = gp.Model("ProductionOptimization")

    # Add decision variables
    # The original model does not specify integrality, so use continuous variables (default)
    x = model.addVar(name="Scooters", lb=0)
    y = model.addVar(name="Bikes", lb=0)

    # Set the objective function
    model.setObjective(200 * x + 300 * y, GRB.MAXIMIZE)

    # Add constraints
    model.addConstr(2 * x + 4 * y <= 5000, name="Constraint1")
    model.addConstr(3 * x + 5 * y <= 6000, name="Constraint2")

    # Optimize the model
    model.optimize()
    return model.objVal if model.status == GRB.OPTIMAL else None

print(optimize_production())