def optimize_repair_schedule(
    max_inspection_time=5000,
    max_fixing_time=20000,
    profit_washing=250,
    profit_freezer=375,
    inspection_time_washing=30,
    inspection_time_freezer=20,
    fixing_time_washing=90,
    fixing_time_freezer=125
):
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("ApplianceRepairOptimization")
    
    # Decision variables: number of washing machines and freezers repaired
    x = m.addVar(vtype=GRB.INTEGER, name="WashingMachines", lb=0)
    y = m.addVar(vtype=GRB.INTEGER, name="Freezers", lb=0)
    
    # Set the objective: maximize profit
    m.setObjective(profit_washing * x + profit_freezer * y, GRB.MAXIMIZE)
    
    # Add constraints
    # Inspection time constraint
    m.addConstr(inspection_time_washing * x + inspection_time_freezer * y <= max_inspection_time, "InspectionTime")
    # Fixing time constraint
    m.addConstr(fixing_time_washing * x + fixing_time_freezer * y <= max_fixing_time, "FixingTime")
    
    # Optimize the model
    m.optimize()
    
    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the maximum profit
        return m.objVal
    else:
        # No feasible solution found
        return None
# Example usage
if __name__ == "__main__":
    max_profit = optimize_repair_schedule()
    if max_profit is not None:
        print(f"Maximum Profit: ${max_profit}")
    else:
        print("No feasible solution found.")