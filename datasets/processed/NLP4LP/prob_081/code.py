def optimize_factory_selection():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("Factory_Optimization")
    
    # Decision variables: number of medium and small factories
    x = m.addVar(vtype=GRB.INTEGER, name="Medium_Factories", lb=0)
    y = m.addVar(vtype=GRB.INTEGER, name="Small_Factories", lb=0)
    
    # Set the objective: minimize total number of factories
    m.setObjective(x + y, GRB.MINIMIZE)
    
    # Add production constraint
    m.addConstr(50 * x + 35 * y >= 250, name="Production_Constraint")
    
    # Add operator constraint
    m.addConstr(3 * x + 2 * y <= 16, name="Operator_Constraint")
    
    # Optimize the model
    m.optimize()
    
    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        return m.objVal
    else:
        return None
# Example usage
if __name__ == "__main__":
    min_factories = optimize_factory_selection()
    if min_factories is not None:
        print(f"Minimum Total Number of Factories: {min_factories}")
    else:
        print("No feasible solution found.")