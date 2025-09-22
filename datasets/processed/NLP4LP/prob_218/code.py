def optimize_air_conditioners():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("AirConditionerOptimization")

    # Decision variables: number of low-power and high-power units
    x = m.addVar(vtype=GRB.INTEGER, name="LowPower")
    y = m.addVar(vtype=GRB.INTEGER, name="HighPower")

    # Set the objective: minimize total units
    m.setObjective(x + y, GRB.MINIMIZE)

    # Add constraints
    # Cooling capacity constraint
    m.addConstr(12 * x + 17 * y >= 250, name="CoolingCapacity")
    # Electricity usage constraint
    m.addConstr(150 * x + 250 * y <= 3400, name="ElectricityLimit")
    # Low-power limit (30% of total)
    m.addConstr(7 * x <= 3 * y, name="LowPowerLimit")
    # Minimum high-power units
    m.addConstr(y >= 7, name="MinHighPower")
    # Non-negativity is implicit in variable definition

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        total_units = m.objVal
        return total_units
    else:
        return None
# Example usage
if __name__ == "__main__":
    min_units = optimize_air_conditioners()
    if min_units is not None:
        print(f"Minimum Total Air Conditioners: {min_units}")
    else:
        print("No feasible solution found.")