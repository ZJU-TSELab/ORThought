def optimize_machine_usage():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("MedicineDeliveryWasteMinimization")

    # Decision variables: usage time of each machine
    t1 = m.addVar(name="t1", lb=0)  # Machine 1 usage time
    t2 = m.addVar(name="t2", lb=0)  # Machine 2 usage time

    # Set objective: minimize total waste
    m.setObjective(0.3 * t1 + 0.5 * t2, GRB.MINIMIZE)

    # Add constraints
    # Medicine delivered to the heart
    m.addConstr(0.5 * t1 + 0.3 * t2 <= 8, name="HeartDelivery")
    # Medicine delivered to the brain
    m.addConstr(0.8 * t1 + 1.0 * t2 >= 4, name="BrainDelivery")

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the optimal total waste
        return m.objVal
    else:
        # No feasible solution
        return None
# Example usage
if __name__ == "__main__":
    min_waste = optimize_machine_usage()
    if min_waste is not None:
        print(f"Minimum Total Waste: {min_waste}")
    else:
        print("No feasible solution found.")