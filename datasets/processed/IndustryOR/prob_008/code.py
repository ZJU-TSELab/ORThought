def optimize_toy_production(
        wood_available=890,
        steel_available=500,
        profit_truck=5,
        profit_airplane=10,
        profit_boat=8,
        profit_train=7,
        M=1000  # Big-M value
):
    import gurobipy as gp
    from gurobipy import GRB

    # Create model
    model = gp.Model("HausToysOptimization")
    model.setParam('OutputFlag', 0)  # Silence output

    # Decision variables
    T = model.addVar(vtype=GRB.INTEGER, name="T")  # Trucks
    A = model.addVar(vtype=GRB.INTEGER, name="A")  # Airplanes
    B = model.addVar(vtype=GRB.INTEGER, name="B")  # Boats
    R = model.addVar(vtype=GRB.INTEGER, name="R")  # Trains

    # Binary variables for logical conditions
    y_T = model.addVar(vtype=GRB.BINARY, name="y_T")
    y_R = model.addVar(vtype=GRB.BINARY, name="y_R")
    y_B = model.addVar(vtype=GRB.BINARY, name="y_B")

    # Objective: maximize profit
    model.setObjective(
        profit_truck * T + profit_airplane * A + profit_boat * B +
        profit_train * R, GRB.MAXIMIZE)

    # Resource constraints
    model.addConstr(12 * T + 20 * A + 15 * B + 10 * R <= wood_available,
                    "Wood")
    model.addConstr(6 * T + 3 * A + 5 * B + 4 * R <= steel_available, "Steel")

    # Boats cannot exceed trains
    model.addConstr(B <= R, "BoatTrainLimit")

    # Logical constraints for trucks and trains (mutual exclusivity)
    model.addConstr(T <= M * y_T, "TruckLogical")
    model.addConstr(R <= M * y_R, "TrainLogical")
    model.addConstr(y_T + y_R <= 1, "MutualExclusion")

    # Logical constraints for boats and airplanes
    model.addConstr(A >= y_B, "AirplaneBoat")
    model.addConstr(B <= y_B * M, "BoatBinary")

    # Optional: enforce non-negativity (default in Gurobi)
    # Variables are already non-negative by default unless specified otherwise

    # Optimize
    model.optimize()

    # Check feasibility
    if model.status == GRB.OPTIMAL:
        return model.objVal
    else:
        return None
if __name__ == "__main__":
    result = optimize_toy_production()
    print(f"Optimal profit: {result}")