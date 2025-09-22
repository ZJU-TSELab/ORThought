def optimize_dogs(max_treats=1500, min_golden=50, max_lab_ratio=0.6):
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("DogSchoolOptimization")
    m.setParam('OutputFlag', 0)  # Silence Gurobi output

    # Decision variables
    L = m.addVar(name="Labradors", vtype=GRB.INTEGER, lb=0)
    G = m.addVar(name="Goldens", vtype=GRB.INTEGER, lb=min_golden)

    # Objective: Maximize total newspapers delivered
    m.setObjective(7 * L + 10 * G, GRB.MAXIMIZE)

    # Constraints
    # Bone treat constraint
    m.addConstr(5 * L + 6 * G <= max_treats, name="TreatsLimit")
    # Golden retriever minimum
    m.addConstr(G >= min_golden, name="MinGoldens")
    # Labrador proportion constraint: L <= 0.6 * (L + G)
    # Rearranged: 2L <= 3G
    m.addConstr(2 * L <= 3 * G, name="LabradorProportion")

    # Optimize
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        total_newspapers = m.objVal
        return total_newspapers
    else:
        return None
# Example usage
if __name__ == "__main__":
    max_newspapers = optimize_dogs()
    if max_newspapers is not None:
        print(f"Maximum Newspapers Delivered: {max_newspapers}")
    else:
        print("No feasible solution found.")