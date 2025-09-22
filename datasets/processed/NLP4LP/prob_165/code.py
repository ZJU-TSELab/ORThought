import gurobipy as gp
from gurobipy import GRB

def minimize_jars(volume_threshold=100000, small_jar_ml=50, large_jar_ml=200):
    """
    Finds the minimum total number of jars (small + large) needed to ship at least
    'volume_threshold' ml of jam, with the constraint that the number of large jars
    cannot exceed the number of small jars.
    
    Args:
        volume_threshold (int): Minimum total volume of jam to ship (default: 100000 ml).
        small_jar_ml (int): Volume of jam in a small jar (default: 50 ml).
        large_jar_ml (int): Volume of jam in a large jar (default: 200 ml).
        
    Returns:
        int or None: The minimum total number of jars if feasible, else None.
    """
    # Create a new model
    model = gp.Model("Minimize_Jars")
    
    # Decision variables: number of small and large jars
    x = model.addVar(name="small_jars", vtype=GRB.INTEGER, lb=0)
    y = model.addVar(name="large_jars", vtype=GRB.INTEGER, lb=0)
    
    # Set objective: minimize total jars
    model.setObjective(x + y, GRB.MINIMIZE)
    
    # Add constraints
    # Volume constraint
    model.addConstr(small_jar_ml * x + large_jar_ml * y >= volume_threshold, "volume_constraint")
    # Preference constraint
    model.addConstr(y <= x, "preference_constraint")
    
    # Optimize the model
    model.optimize()
    
    # Check if a feasible solution was found
    if model.status == GRB.OPTIMAL:
        total_jars = int(x.X + y.X)
        return total_jars
    else:
        return None
# Example usage 
if __name__ == "__main__":
    min_jars = minimize_jars()
    if min_jars is not None:
        print(f"Minimum Total Jars: {min_jars}")
    else:
        print("No feasible solution found.")