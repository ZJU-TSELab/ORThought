def optimize_coal_distribution(supply_A=80,
                               supply_B=100,
                               demand_1=55,
                               demand_2=75,
                               demand_3=50):
    import gurobipy as gp
    from gurobipy import GRB

    # Create a new model
    model = gp.Model("Coal_Distribution_Minimize_TonKilometers")

    # Decision variables: amount of coal shipped from each yard to each area
    x_A1 = model.addVar(lb=0, name="x_A1")
    x_A2 = model.addVar(lb=0, name="x_A2")
    x_A3 = model.addVar(lb=0, name="x_A3")
    x_B1 = model.addVar(lb=0, name="x_B1")
    x_B2 = model.addVar(lb=0, name="x_B2")
    x_B3 = model.addVar(lb=0, name="x_B3")

    # Set objective: minimize total ton-kilometers
    model.setObjective(
        10 * x_A1 + 5 * x_A2 + 6 * x_A3 + 4 * x_B1 + 8 * x_B2 + 15 * x_B3,
        GRB.MINIMIZE)

    # Supply constraints
    model.addConstr(x_A1 + x_A2 + x_A3 >= supply_A, "Supply_A")
    model.addConstr(x_B1 + x_B2 + x_B3 >= supply_B, "Supply_B")

    # Demand constraints
    model.addConstr(x_A1 + x_B1 == demand_1, "Demand_1")
    model.addConstr(x_A2 + x_B2 == demand_2, "Demand_2")
    model.addConstr(x_A3 + x_B3 == demand_3, "Demand_3")

    # Optimize the model
    model.optimize()

    # Check if a feasible solution was found
    if model.status == GRB.OPTIMAL:
        return model.objVal
    else:
        return None
if __name__ == "__main__":
    result = optimize_coal_distribution()
    if result is not None:
        print(f"Optimal total ton-kilometers: {result}")
    else:
        print("No feasible solution found.")