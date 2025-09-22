def optimize_keyboard_production():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("KeyboardProduction")
    
    # Decision variable: y (number of standard keyboards)
    # Since y must be integer and >= 30
    y = m.addVar(name="y", lb=30, vtype=GRB.INTEGER)
    
    # x is determined by y: x = 5 * y
    # No need to define x as a variable, as it's dependent
    
    # Set the objective: maximize total keyboards = x + y = 5y + y = 6y
    m.setObjective(6 * y, GRB.MAXIMIZE)
    
    # Add resource constraints
    # Plastic constraint: 5x + 2y <= 1000
    # Substitute x = 5y: 25y + 2y <= 1000 => 27y <= 1000
    m.addConstr(27 * y <= 1000, name="Plastic")
    
    # Solder constraint: 2x + y <= 250
    # Substitute x = 5y: 10y + y <= 250 => 11y <= 250
    m.addConstr(11 * y <= 250, name="Solder")
    
    # Optimize the model
    m.optimize()
    
    # Check if a feasible solution exists
    if m.status == GRB.OPTIMAL:
        optimal_y = y.X
        optimal_x = 5 * optimal_y
        total_keyboards = 6 * optimal_y
        return total_keyboards
    else:
        # No feasible solution
        return None
# Example usage
if __name__ == "__main__":
    max_keyboards = optimize_keyboard_production()
    if max_keyboards is not None:
        print(f"Maximum Total Keyboards Produced: {max_keyboards}")
    else:
        print("No feasible solution found.")