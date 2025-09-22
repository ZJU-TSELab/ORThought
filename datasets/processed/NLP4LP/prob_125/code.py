def optimize_lab_hours(
    production_heart=20000,
    production_lung=30000,
    max_worker_hours=1500,
    lab1_sessions_hours=3,
    lab2_sessions_hours=5,
    lab1_heart_rate=20,
    lab1_lung_rate=30,
    lab2_heart_rate=30,
    lab2_lung_rate=40
):
    import gurobipy as gp
    from gurobipy import GRB

    # Create a new model
    model = gp.Model("Minimize_Lab_Time")

    # Decision variables: number of sessions at each lab
    x1 = model.addVar(name="x1", lb=0)
    x2 = model.addVar(name="x2", lb=0)

    # Set objective: minimize total hours
    model.setObjective(
        lab1_sessions_hours * x1 + lab2_sessions_hours * x2,
        GRB.MINIMIZE
    )

    # Add production constraints
    model.addConstr(
        lab1_heart_rate * x1 + lab2_heart_rate * x2 >= production_heart,
        name="Heart_Production"
    )
    model.addConstr(
        lab1_lung_rate * x1 + lab2_lung_rate * x2 >= production_lung,
        name="Lung_Production"
    )

    # Add labor hours constraint
    model.addConstr(
        lab1_sessions_hours * x1 + lab2_sessions_hours * x2 <= max_worker_hours,
        name="Worker_Hours"
    )

    # Optimize the model
    model.optimize()

    # Check if a feasible solution was found
    if model.status == GRB.OPTIMAL:
        total_time = model.objVal
        return total_time
    else:
        return None

# Example usage
if __name__ == "__main__":
    min_time = optimize_lab_hours()
    if min_time is not None:
        print(f"Minimum Total Lab Time: {min_time}")
    else:
        print("No feasible solution found.")