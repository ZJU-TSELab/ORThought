def optimize_truck_dispatch(
        cost_A=200,  # freight cost per truck from warehouse A
        cost_B=160,  # freight cost per truck from warehouse B
        min_A=240,  # minimum raw material A pieces
        min_B=80,  # minimum raw material B kg
        min_C=120  # minimum raw material C tons
):
    import gurobipy as gp
    from gurobipy import GRB

    # Create a new model
    model = gp.Model("Truck_Dispatch_Optimization")

    # Decision variables: number of trucks from warehouses A and B
    x_A = model.addVar(vtype=GRB.INTEGER, lb=0, name="x_A")
    x_B = model.addVar(vtype=GRB.INTEGER, lb=0, name="x_B")

    # Set objective: minimize total freight cost
    model.setObjective(cost_A * x_A + cost_B * x_B, GRB.MINIMIZE)

    # Add constraints for raw materials
    # Raw material A
    model.addConstr(4 * x_A + 7 * x_B >= min_A, "Raw_A")
    # Raw material B
    model.addConstr(2 * x_A + 2 * x_B >= min_B, "Raw_B")
    # Raw material C
    model.addConstr(6 * x_A + 2 * x_B >= min_C, "Raw_C")

    # Optimize the model
    model.optimize()

    # Check if a feasible solution was found
    if model.status == GRB.OPTIMAL:
        # Return the optimal total freight cost
        return model.objVal
    else:
        # No feasible solution found
        return None
if __name__ == "__main__":
    result = optimize_truck_dispatch()
    if result is not None:
        print(f"Optimal total freight cost: {result}")
    else:
        print("No feasible solution found.")