def optimize_office_desks(budget=2000, space_limit=200, long_desk_cost=300, short_desk_cost=100,
                          long_desk_space=10, short_desk_space=4, long_desk_seats=6, short_desk_seats=2):
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("Office_Desks_Optimization")
    
    # Decision variables: number of long and short desks
    x = m.addVar(vtype=GRB.INTEGER, name="LongDesks", lb=0)
    y = m.addVar(vtype=GRB.INTEGER, name="ShortDesks", lb=0)
    
    # Set the objective: maximize total seating
    m.setObjective(long_desk_seats * x + short_desk_seats * y, GRB.MAXIMIZE)
    
    # Add budget constraint
    m.addConstr(long_desk_cost * x + short_desk_cost * y <= budget, "BudgetConstraint")
    
    # Add space constraint
    m.addConstr(long_desk_space * x + short_desk_space * y <= space_limit, "SpaceConstraint")
    
    # Optimize the model
    m.optimize()
    
    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the maximum seating capacity
        return m.objVal
    else:
        # No feasible solution
        return None
# Example usage
if __name__ == "__main__":
    max_seating = optimize_office_desks()
    if max_seating is not None:
        print(f"Maximum Seating Capacity: {max_seating}")
    else:
        print("No feasible solution found.")