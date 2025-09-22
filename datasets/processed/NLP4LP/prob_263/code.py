def optimize_vaccine_production(antibiotic_available=35000, gelatine_first=20, gelatine_second=60,
                                antibiotic_first=30, antibiotic_second=65, min_second=40):
    import gurobipy as gp
    from gurobipy import GRB

    # Create a new model
    model = gp.Model("Vaccine_Production_Min_Gelatine")

    # Decision variables: number of first and second dose vaccines
    x1 = model.addVar(vtype=GRB.INTEGER, name="First_Dose")
    x2 = model.addVar(vtype=GRB.INTEGER, name="Second_Dose")

    # Set objective: minimize total gelatine used
    model.setObjective(gelatine_first * x1 + gelatine_second * x2, GRB.MINIMIZE)

    # Add constraints
    # Antibiotic availability constraint
    model.addConstr(antibiotic_first * x1 + antibiotic_second * x2 <= antibiotic_available, "Antibiotic_Limit")
    # Production order constraint: first-dose > second-dose
    model.addConstr(x1 >= x2 + 1, "Order_Constraint")
    # Minimum second-dose vaccines
    model.addConstr(x2 >= min_second, "Min_Second_Dose")
    # Non-negativity is implicit in variable definition

    # Optimize the model
    model.optimize()

    # Check if a feasible solution was found
    if model.status == GRB.OPTIMAL:
        # Return the optimal total gelatine used
        return model.objVal
    else:
        # No feasible solution
        return None

# Example usage
if __name__ == "__main__":
    result = optimize_vaccine_production()
    print(f"Optimal total gelatine used: {result}")