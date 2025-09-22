import gurobipy as gp
from gurobipy import GRB


def solve_bin_packing(
    item_loads={1: 6, 2: 7, 3: 8, 4: 3, 5: 2, 6: 4, 7: 5},
    box_capacity=10
):
    """
    Models and solves the Bin Packing problem.
    """
    # --- 1. Model Creation ---
    model = gp.Model("BinPacking")

    # --- 2. Sets and Parameters ---
    items = list(item_loads.keys())
    # The number of bins cannot exceed the number of items
    bins = range(1, len(items) + 1)

    # --- 3. Decision Variables ---
    # x[b] = 1 if bin b is used, 0 otherwise
    x = model.addVars(bins, vtype=GRB.BINARY, name="BinUsed")

    # y[i,b] = 1 if item i is packed in bin b, 0 otherwise
    y = model.addVars(items, bins, vtype=GRB.BINARY, name="ItemInBin")

    # --- 4. Objective Function ---
    # Minimize the number of bins used
    model.setObjective(gp.quicksum(x[b] for b in bins), GRB.MINIMIZE)

    # --- 5. Constraints ---
    # Constraint 1: Each item must be packed in exactly one bin
    for i in items:
        model.addConstr(gp.quicksum(y[i, b] for b in bins) == 1,
                        name=f"item_assign_{i}")

    # Constraint 2: The total load of items in each bin must not exceed its capacity.
    # This also links the y and x variables: if a bin is not used (x[b]=0),
    # no items can be placed in it (sum of y[i,b] must be 0).
    for b in bins:
        model.addConstr(
            gp.quicksum(item_loads[i] * y[i, b] for i in items) <= box_capacity * x[b],
            name=f"bin_capacity_{b}"
        )

    # --- 6. Solve the Model ---
    model.setParam("OutputFlag", 0)  # Suppress Gurobi output
    model.optimize()

    # --- 7. Return Results ---
    if model.status == GRB.OPTIMAL:
        # Gurobi objective value can be a float, so we cast to int for bin packing
        return {"status": "optimal", "obj": int(model.ObjVal)}
    else:
        return {"status": f"{model.status}"}


# Run the solver function
if __name__ == "__main__":
    result = solve_bin_packing()
    print(result)