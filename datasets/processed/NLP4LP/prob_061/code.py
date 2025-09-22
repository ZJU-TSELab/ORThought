def optimize_branches():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("BankBranches")

    # Decision variables: number of small and large branches
    x = m.addVar(vtype=GRB.INTEGER, name="small_branches", lb=0)
    y = m.addVar(vtype=GRB.INTEGER, name="large_branches", lb=0)

    # Set the objective: minimize total number of branches
    m.setObjective(x + y, GRB.MINIMIZE)

    # Add customer service constraint
    m.addConstr(50 * x + 100 * y >= 1200, name="CustomerService")

    # Add teller constraint
    m.addConstr(10 * x + 15 * y <= 200, name="TellerAvailability")

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the optimal value of the objective function
        return m.objVal
    else:
        # No feasible solution found
        return None
# Example usage
if __name__ == "__main__":
    min_branches = optimize_branches()
    if min_branches is not None:
        print(f"Minimum Total Number of Branches: {min_branches}")
    else:
        print("No feasible solution found.")