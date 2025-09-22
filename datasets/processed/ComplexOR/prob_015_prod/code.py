def optimize_profit(a=None, c=None, u=None, b=None):
    """
    Solves the described optimization problem using Gurobipy.
    
    Parameters:
    - a: list of a[j] parameters
    - c: list of c[j] profit coefficients
    - u: list of upper bounds u[j]
    - b: global resource constraint parameter
    
    Returns:
    - The optimal objective value if feasible, else None.
    """
    import gurobipy as gp
    from gurobipy import GRB

    # Default data based on the sample provided
    if a is None:
        a = [3, 1, 2]
    if c is None:
        c = [5, 10, 8]
    if u is None:
        u = [4, 6, 3]
    if b is None:
        b = 4

    P = range(len(a))  # set P indices

    # Create model
    model = gp.Model("Maximize_Profit")
    model.Params.OutputFlag = 0  # Silence output

    # Decision variables X[j]
    X = model.addVars(P, lb=0, ub=u, vtype=GRB.CONTINUOUS, name="X")

    # Objective: maximize sum of c[j]*X[j]
    model.setObjective(gp.quicksum(c[j] * X[j] for j in P), GRB.MAXIMIZE)

    # Constraint: sum of (1/a[j])*X[j] <= b
    model.addConstr(
        gp.quicksum((1.0 / a[j]) * X[j] for j in P) <= b,
        name="ResourceConstraint"
    )

    # Optimize
    model.optimize()

    # Check feasibility and return the optimal value
    if model.status == GRB.OPTIMAL:
        return model.objVal
    else:
        return None
if __name__ == "__main__":
    result = optimize_profit()
    if result is not None:
        print(f"Optimal profit: {result}")
    else:
        print("No feasible solution found.")