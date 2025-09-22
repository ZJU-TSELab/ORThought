def minimize_pollution(M=20):
    from gurobipy import Model, GRB

    # Create a new model
    model = Model("Minimize Pollution")

    # Decision variables
    y_m = model.addVar(vtype=GRB.BINARY, name="motorcycle_method")
    y_s = model.addVar(vtype=GRB.BINARY, name="small_truck_method")
    y_l = model.addVar(vtype=GRB.BINARY, name="large_truck_method")

    x_m = model.addVar(vtype=GRB.INTEGER, lb=0, name="motorcycle_trips")
    x_s = model.addVar(vtype=GRB.INTEGER, lb=0, name="small_truck_trips")
    x_l = model.addVar(vtype=GRB.INTEGER, lb=0, name="large_truck_trips")

    # Set objective: minimize total pollution
    model.setObjective(40 * x_m + 70 * x_s + 100 * x_l, GRB.MINIMIZE)

    # Constraints
    model.addConstr(y_m + y_s + y_l == 2, "Method_Selection")
    model.addConstr(x_m <= 8, "Motorcycle_Trip_Limit")
    model.addConstr(x_m <= M * y_m, "Motorcycle_Method_Activation")
    model.addConstr(x_s <= M * y_s, "SmallTruck_Method_Activation")
    model.addConstr(x_l <= M * y_l, "LargeTruck_Method_Activation")
    model.addConstr(10 * x_m + 20 * x_s + 50 * x_l >= 300,
                    "Transport_Requirement")
    model.addConstr(x_m + x_s + x_l <= 20, "Total_Trips_Limit")

    # Optimize the model
    model.optimize()

    # Check if a feasible solution was found
    if model.status == GRB.OPTIMAL:
        return model.objVal
    else:
        return None
if __name__ == "__main__":
    result = minimize_pollution()
    if result is not None:
        print(f"Optimal total pollution: {result}")
    else:
        print("No feasible solution found.")