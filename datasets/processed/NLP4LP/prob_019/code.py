def optimize_factory_layout(space_limit=100, max_cost=5000, max_labor=2000):
    import gurobipy as gp
    from gurobipy import GRB

    # Create a new model
    model = gp.Model("Factory_Layout_Maximize_Revenue")

    # Decision variables: space allocated to phones and laptops
    x = model.addVar(name="Phones_Space", lb=0)
    y = model.addVar(name="Laptops_Space", lb=0)

    # Set the objective: maximize total revenue
    model.setObjective(50 * x + 70 * y, GRB.MAXIMIZE)

    # Add constraints
    # Space constraint
    model.addConstr(x + y <= space_limit, name="SpaceLimit")
    # Cost constraint
    model.addConstr(12 * x + 15 * y <= max_cost, name="CostLimit")
    # Labor constraint
    model.addConstr(2 * x + 3 * y <= max_labor, name="LaborLimit")

    # Optimize the model
    model.optimize()

    # Check if a feasible solution was found
    if model.status == GRB.OPTIMAL:
        # Return the optimal revenue
        return model.objVal
    else:
        # No feasible solution found
        return None
# Example usage
if __name__ == "__main__":
    max_revenue = optimize_factory_layout()
    if max_revenue is not None:
        print(f"Maximum Revenue: {max_revenue}")
    else:
        print("No feasible solution found.")