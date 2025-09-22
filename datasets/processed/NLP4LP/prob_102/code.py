def optimize_vaccine_production(
    total_mrna=20000,
    min_children=50,
    adult_ratio=0.7,
    children_mrna=50,
    children_fever=50,
    adult_mrna=75,
    adult_fever=75
):
    import gurobipy as gp
    from gurobipy import GRB

    # Create a new model
    model = gp.Model("Vaccine_Production_Optimization")
    
    # Decision variables: number of children's and adult vaccines
    x = model.addVar(vtype=GRB.INTEGER, lb=0, name="Children")
    y = model.addVar(vtype=GRB.INTEGER, lb=0, name="Adult")
    
    # Set the objective: minimize total fever suppressant
    model.setObjective(children_fever * x + adult_fever * y, GRB.MINIMIZE)
    
    # Add resource constraint (mRNA availability)
    model.addConstr(children_mrna * x + adult_mrna * y <= total_mrna, "mRNA_constraint")
    
    # Add ratio constraint: y >= (7/3) * x
    model.addConstr(y >= (7/3) * x, "adult_ratio_constraint")
    
    # Add minimum children's vaccines constraint
    model.addConstr(x >= min_children, "min_children_constraint")
    
    # Optimize the model
    model.optimize()
    
    # Check if a feasible solution was found
    if model.status == GRB.OPTIMAL:
        # Return the minimum total fever suppressant used
        return model.objVal
    else:
        # No feasible solution found
        return None
# Example usage
if __name__ == "__main__":
    min_fever_suppressant = optimize_vaccine_production()
    if min_fever_suppressant is not None:
        print(f"Minimum Total Fever Suppressant Used: {min_fever_suppressant}")
    else:
        print("No feasible solution found.")