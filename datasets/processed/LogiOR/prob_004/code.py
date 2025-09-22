import gurobipy as gp
from gurobipy import GRB


def solve_variable_bin_packing(
    box_capacity={1: 5, 2: 9, 3: 8, 4: 7, 5: 7, 6: 8},
    item_loads={1: 6, 2: 7, 3: 8, 4: 3, 5: 2, 6: 4, 7: 5},
):
    """
    Models and solves the Bin Packing problem with variable bin capacities.
    """
    # --- 1. Model Creation ---
    model = gp.Model("BinPackingVariableCapacity")

    # --- 2. Sets ---
    # Derive sets from the keys of the input data for flexibility
    boxes = list(box_capacity.keys())
    items = list(item_loads.keys())

    # --- 3. Decision Variables ---
    # x[b] = 1 if box b is used, 0 otherwise
    x = model.addVars(boxes, vtype=GRB.BINARY, name="BoxUsed")

    # y[i,b] = 1 if item i is packed in box b, 0 otherwise
    y = model.addVars(items, boxes, vtype=GRB.BINARY, name="ItemInBox")

    # --- 4. Objective Function ---
    # Minimize the number of boxes used
    model.setObjective(gp.quicksum(x[b] for b in boxes), GRB.MINIMIZE)

    # --- 5. Constraints ---
    # Constraint 1: Each item must be packed in exactly one box
    for i in items:
        model.addConstr(gp.quicksum(y[i, b] for b in boxes) == 1,
                        name=f"item_assign_{i}")

    # Constraint 2: The total load of items in each box must not exceed its capacity.
    # This also links the y and x variables.
    for b in boxes:
        model.addConstr(
            gp.quicksum(item_loads[i] * y[i, b] for i in items) <= box_capacity[b] * x[b],
            name=f"box_capacity_{b}"
        )

    # --- 6. Solve the Model ---
    # model.setParam("OutputFlag", 0)  # Suppress Gurobi output
    model.optimize()

    # --- 7. Return Results ---
    if model.status == GRB.OPTIMAL:
        # The objective value for bin packing is an integer
        return {"status": "optimal", "obj": int(model.ObjVal)}
    else:
        return {"status": f"{model.status}"}


# Run the solver function
if __name__ == "__main__":
    result = solve_variable_bin_packing()
    print(result)