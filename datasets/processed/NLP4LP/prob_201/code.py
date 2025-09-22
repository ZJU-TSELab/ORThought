import gurobipy as gp
from gurobipy import GRB

def optimize_supplements(
    cost_A=2,        # Cost per pill of supplement A
    cost_B=3,        # Cost per pill of supplement B
    iron_A=5,        # Iron units in supplement A
    calcium_A=10,     # Calcium units in supplement A
    iron_B=4,        # Iron units in supplement B
    calcium_B=15,     # Calcium units in supplement B
    min_iron=40,     # Minimum iron requirement
    min_calcium=50   # Minimum calcium requirement
):
    # Create a new model
    model = gp.Model("SupplementsOptimization")
    
    # Add decision variables (integer, non-negative)
    x_A = model.addVar(vtype=GRB.INTEGER, lb=0, name="x_A")
    x_B = model.addVar(vtype=GRB.INTEGER, lb=0, name="x_B")
    
    # Set the objective: minimize total cost
    model.setObjective(cost_A * x_A + cost_B * x_B, GRB.MINIMIZE)
    
    # Add constraints
    # Iron constraint
    model.addConstr(iron_A * x_A + iron_B * x_B >= min_iron, "IronRequirement")
    # Calcium constraint
    model.addConstr(calcium_A * x_A + calcium_B * x_B >= min_calcium, "CalciumRequirement")
    
    # Optimize the model
    model.optimize()
    
    # Check if a feasible solution was found
    if model.status == GRB.OPTIMAL:
        # Return the optimal total cost
        return model.objVal
    else:
        # No feasible solution found
        return None
# Example usage
if __name__ == "__main__":
    min_cost = optimize_supplements()
    if min_cost is not None:
        print(f"Minimum Cost: {min_cost}")
    else:
        print("No feasible solution found.")