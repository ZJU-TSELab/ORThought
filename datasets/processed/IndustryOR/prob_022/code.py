def hongdou_factory_optimization(labor_per_unit=[3, 2, 6],
                                 material_per_unit=[4, 3, 6],
                                 selling_price=[120, 80, 180],
                                 variable_cost=[60, 40, 80],
                                 labor_available=1500,
                                 material_available=1600,
                                 fixed_costs=[2000, 1500, 1000]):
    from gurobipy import Model, GRB

    n = len(labor_per_unit)  # number of products

    # Net profit per unit for each product
    profit_per_unit = [selling_price[i] - variable_cost[i] for i in range(n)]
    total_fixed_cost = sum(fixed_costs)

    try:
        # --- Model Initialization ---
        m = Model()
        m.setParam('OutputFlag', 0)

        # --- Decision variables ---
        # number of units produced for product i
        x = m.addVars(n, vtype=GRB.INTEGER, name="product_num")

        # --- Objective ---
        # maximize total profit
        m.setObjective(
            sum(profit_per_unit[i] * x[i]
                for i in range(n)) - total_fixed_cost, GRB.MAXIMIZE)

        # --- Constraints ---
        # Labor constraint
        m.addConstr(
            sum(labor_per_unit[i] * x[i] for i in range(n)) <= labor_available,
            "Labor")

        # Material constraint
        m.addConstr(
            sum(material_per_unit[i] * x[i] for i in range(n))
            <= material_available, "Material")

        # --- Optimize the model ---
        m.optimize()

        if m.status == GRB.OPTIMAL:
            return m.objVal
        else:
            return None
    except Exception:
        return None

if __name__ == "__main__":
    result = hongdou_factory_optimization()
    if result is not None:
        print(f"Optimal profit: {result}")
    else:
        print("No optimal solution found.")