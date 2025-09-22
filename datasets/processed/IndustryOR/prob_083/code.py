def optimize_candidate_selection():
    from gurobipy import Model, GRB

    # Candidate data
    salaries = {'A': 8100, 'B': 20000, 'C': 21000, 'D': 3000, 'E': 8000}
    # Initialize model
    m = Model("Candidate_Selection")
    m.setParam('OutputFlag', 0)  # Suppress output

    # Decision variables
    y_A = m.addVar(vtype=GRB.BINARY, name='A')
    y_B = m.addVar(vtype=GRB.BINARY, name='B')
    y_C = m.addVar(vtype=GRB.BINARY, name='C')
    y_D = m.addVar(vtype=GRB.BINARY, name='D')
    y_E = m.addVar(vtype=GRB.BINARY, name='E')

    # Update model to integrate variables
    m.update()

    # Objective: Minimize total salary
    m.setObjective(
        salaries['A'] * y_A + salaries['B'] * y_B + salaries['C'] * y_C +
        salaries['D'] * y_D + salaries['E'] * y_E, GRB.MINIMIZE)

    # Constraints
    # Max 3 hires
    m.addConstr(y_A + y_B + y_C + y_D + y_E <= 3, "max_hires")
    # At least 2 hires
    m.addConstr(y_A + y_B + y_C + y_D + y_E >= 2, "min_hires")
    # Budget constraint
    m.addConstr(
        salaries['A'] * y_A + salaries['B'] * y_B + salaries['C'] * y_C +
        salaries['D'] * y_D + salaries['E'] * y_E <= 35000, "budget")
    # Qualification constraint: at least one with Master's or Doctoral degree
    m.addConstr(y_B + y_C >= 1, "qualification")
    # Experience constraint
    m.addConstr(3 * y_A + 10 * y_B + 4 * y_C + 3 * y_D + 7 * y_E >= 12,
                "experience")
    # Skill equivalence constraint: at most one of A and E
    m.addConstr(y_A + y_E <= 1, "skill_equivalence")

    # Optimize
    m.optimize()

    # Check feasibility and return result
    if m.status == GRB.OPTIMAL:
        return m.objVal
    else:
        return None
if __name__ == "__main__":
    result = optimize_candidate_selection()
    if result is not None:
        print(f"Optimal total salary: {result}")
    else:
        print("No feasible solution found.")