def optimize_mail_transport(
    max_sub_trips=6,
    min_total_mail=1000,
    mail_per_sub=100,
    mail_per_boat=80,
    gas_per_sub=30,
    gas_per_boat=25
):
    import gurobipy as gp
    from gurobipy import GRB

    # Create a new model
    model = gp.Model("MailTransportMinGas")

    # Decision variables: number of trips by submarine and boat
    x = model.addVar(vtype=GRB.INTEGER, name="submarine_trips")
    y = model.addVar(vtype=GRB.INTEGER, name="boat_trips")

    # Set objective: minimize total gas
    model.setObjective(gas_per_sub * x + gas_per_boat * y, GRB.MINIMIZE)

    # Add constraints
    model.addConstr(x <= max_sub_trips, "max_sub_trips")
    model.addConstr(mail_per_sub * x + mail_per_boat * y >= min_total_mail, "mail_requirement")
    model.addConstr(y >= x, "boat_at_least_half")  # y >= x

    # Non-negativity constraints are implicit in variable definitions

    # Optimize the model
    model.optimize()

    # Check if a feasible solution was found
    if model.status == GRB.OPTIMAL:
        # Return the optimal total gas used
        return model.objVal
    else:
        # No feasible solution
        return None
# Example usage
if __name__ == "__main__":
    total_gas = optimize_mail_transport()
    if total_gas is not None:
        print(f"Minimum Total Gas Consumption: {total_gas}")
    else:
        print("No feasible solution found.")