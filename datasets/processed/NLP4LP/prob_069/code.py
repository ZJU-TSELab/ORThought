import gurobipy as gp
from gurobipy import GRB

def optimize_firefighters(
    hours_required=300,
    hours_regular=10,
    hours_emergency=6,
    cost_regular=300,
    cost_emergency=100,
    budget=7000
):
    # Create a new model
    model = gp.Model("FireFighterOptimization")
    
    # Add decision variables: number of regular and emergency fire fighters
    R = model.addVar(vtype=GRB.INTEGER, name="Regular_Firefighters", lb=0)
    E = model.addVar(vtype=GRB.INTEGER, name="Emergency_Firefighters", lb=0)
    
    # Set the objective: minimize total number of fire fighters
    model.setObjective(R + E, GRB.MINIMIZE)
    
    # Add constraints
    # Hours constraint
    model.addConstr(hours_regular * R + hours_emergency * E >= hours_required, "HoursRequirement")
    
    # Budget constraint
    model.addConstr(cost_regular * R + cost_emergency * E <= budget, "BudgetLimit")
    
    # Optimize the model
    model.optimize()
    
    # Check if a feasible solution was found
    if model.status == GRB.OPTIMAL:
        # Return the total number of fire fighters hired
        total_firefighters = R.X + E.X
        return total_firefighters
    else:
        # No feasible solution found
        return None
# Example usage
if __name__ == "__main__":
    total_firefighters = optimize_firefighters()
    if total_firefighters is not None:
        print(f"Total Fire Fighters Hired: {total_firefighters}")
    else:
        print("No feasible solution found.")