def optimize_factory_selection(
    min_phones=3000,
    max_managers=260,
    rural_phones=100,
    urban_phones=200,
    rural_managers=8,
    urban_managers=20
):
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("Factory_Optimization")
    m.setParam('OutputFlag', 0)  # Suppress Gurobi output

    # Decision variables: number of rural and urban factories
    R = m.addVar(vtype=GRB.INTEGER, name="Rural_Factories", lb=0)
    U = m.addVar(vtype=GRB.INTEGER, name="Urban_Factories", lb=0)

    # Set the objective: minimize total number of factories
    m.setObjective(R + U, GRB.MINIMIZE)

    # Add production constraint
    m.addConstr(rural_phones * R + urban_phones * U >= min_phones, "Production_Constraint")

    # Add manager constraint
    m.addConstr(rural_managers * R + urban_managers * U <= max_managers, "Manager_Constraint")

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        return m.objVal
    else:
        return None
# Example usage
if __name__ == "__main__":
    min_factories = optimize_factory_selection()
    if min_factories is not None:
        print(f"Minimum Total Number of Factories: {min_factories}")
    else:
        print("No feasible solution found.")