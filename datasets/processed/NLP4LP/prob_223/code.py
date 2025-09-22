def optimize_hospital_shifts(
    hours_required=500,
    technician_hours_per_shift=8,
    technician_cost=300,
    researcher_hours_per_shift=5,
    researcher_cost=100,
    budget=14000
):
    import gurobipy as gp
    from gurobipy import GRB

    # Create a new model
    model = gp.Model("Hospital_Shifts_Optimization")

    # Decision variables: number of technician and researcher shifts
    T = model.addVar(vtype=GRB.INTEGER, name="TechnicianShifts")
    R = model.addVar(vtype=GRB.INTEGER, name="ResearcherShifts")

    # Set objective: minimize total number of workers (shifts)
    model.setObjective(T + R, GRB.MINIMIZE)

    # Add constraints
    # Hours constraint
    model.addConstr(technician_hours_per_shift * T >= hours_required, "HoursRequirement")
    # Budget constraint
    model.addConstr(technician_cost * T + researcher_cost * R <= budget, "BudgetLimit")
    # Regulatory constraint
    model.addConstr(T == 2 * R, "RegulatoryConstraint")
    # Non-negativity is implicit in variable definition

    # Optimize the model
    model.optimize()

    # Check if a feasible solution was found
    if model.status == GRB.OPTIMAL:
        total_shifts = T.X + R.X
        return total_shifts
    else:
        return None
# Example usage
if __name__ == "__main__":
    total_shifts = optimize_hospital_shifts()
    if total_shifts is not None:
        print(f"Minimum Total Shifts: {total_shifts}")
    else:
        print("No feasible solution found.")