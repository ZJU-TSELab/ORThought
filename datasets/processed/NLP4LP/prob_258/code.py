def optimize_mail_delivery():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("MailDeliveryOptimization")

    # Decision variables: number of trips by runners and canoers
    R = m.addVar(name="R", lb=4, vtype=GRB.INTEGER)  # at least 4 runners
    C = m.addVar(name="C", lb=0, vtype=GRB.INTEGER)

    # Set the objective: maximize total mail delivered
    m.setObjective(3 * R + 10 * C, GRB.MAXIMIZE)

    # Add constraints
    # Time constraint
    m.addConstr(4 * R + 2 * C <= 200, name="TimeLimit")
    # Canoe usage limit (33%)
    m.addConstr(6.7 * C <= 0.99 * R, name="CanoeLimit")

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the maximum total mail delivered
        return m.objVal
    else:
        # No feasible solution
        return None
# Example usage
if __name__ == "__main__":
    max_mail = optimize_mail_delivery()
    if max_mail is not None:
        print(f"Maximum Mail Delivered: {max_mail} units")
    else:
        print("No feasible solution found.")