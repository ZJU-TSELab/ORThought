from gurobipy import Model, GRB, quicksum


def solve_factory_scheduling():
    # --- 模型初始化 ---
    model = Model("FactoryProductionScheduling")

    # --- 集合定义 ---
    products = ["I", "II", "III"]
    quarters = list(range(4))  # 0: Q1, 1: Q2, 2: Q3, 3: Q4

    # --- 参数定义 ---
    demand = {
        ("I", 0): 1500,
        ("I", 1): 1000,
        ("I", 2): 2000,
        ("I", 3): 1200,
        ("II", 0): 1500,
        ("II", 1): 1500,
        ("II", 2): 1200,
        ("II", 3): 1500,
        ("III", 0): 1000,
        ("III", 1): 2000,
        ("III", 2): 1500,
        ("III", 3): 2500,
    }

    initial_inventory = {prod: 0 for prod in products}  # 期初库存
    ending_inventory_target = {prod: 150 for prod in products}  # 第四季度末库存目标

    production_hours_per_quarter = 15000  # 每季度可用生产工时

    hours_per_unit = {  # 每单位产品所需工时
        "I": 2,
        "II": 4,
        "III": 3,
    }

    # 产品I在第二季度 (索引1) 不能生产
    production_restriction_product = "I"
    production_restriction_quarter = 1

    backlog_cost_per_unit_per_quarter = { # 单位产品每季度延期赔偿
        "I": 20,
        "II": 20,
        "III": 10,
    }

    inventory_cost_per_unit_per_quarter = 5  # 单位产品每季度库存成本

    # --- 决策变量 ---
    # P[p, q]: 在季度q生产产品p的数量
    P = model.addVars(products,
                      quarters,
                      name="Production",
                    #   vtype=GRB.CONTINUOUS,
                      vtype=GRB.INTEGER,
                      lb=0)
    # I[p, q]: 在季度q末产品p的库存量
    I = model.addVars(products,
                      quarters,
                      name="Inventory",
                    #   vtype=GRB.CONTINUOUS,
                      vtype=GRB.INTEGER,
                      lb=0)
    # B[p, q]: 在季度q末产品p的积压订单量
    B = model.addVars(products,
                      quarters,
                      name="Backlog",
                    #   vtype=GRB.CONTINUOUS,
                      vtype=GRB.INTEGER,
                      lb=0)

    # --- 目标函数: 最小化总成本 (赔偿成本 + 库存成本) ---
    total_backlog_cost = quicksum(
        B[p, q] * backlog_cost_per_unit_per_quarter[p] for p in products
        for q in quarters)
    total_inventory_cost = quicksum(
        I[p, q] * inventory_cost_per_unit_per_quarter for p in products
        for q in quarters)

    model.setObjective(total_backlog_cost + total_inventory_cost, GRB.MINIMIZE)

    # --- 约束条件 ---
    for q in quarters:
        # 1. 生产能力约束 (每季度总工时)
        model.addConstr(quicksum(P[p, q] * hours_per_unit[p] for p in products)
                        <= production_hours_per_quarter,
                        name=f"Capacity_Q{q+1}")

        for p in products:
            # 2. 库存平衡约束
            # 期初库存 (I_prev) + 本期生产 (P) - 本期需求 (D) = 期末库存 (I_curr) - 期末积压 (B_curr)
            # I_prev - B_prev + P = D + I_curr - B_curr (如果B代表的是净效应)
            # 我们使用: I[p,q-1] + P[p,q] - Demand[p,q] = I[p,q] - B[p,q]
            # 这意味着 I[p,q] 和 B[p,q] 中至少一个为0 (或模型会趋向于此以最小化成本)

            inventory_at_start_of_quarter = I[
                p, q - 1] if q > 0 else initial_inventory[p]
            # 积压订单是上期末的，本期需要优先满足
            # 修正库存平衡方程：
            # (上期末库存 - 上期末积压) + 本期生产 - 本期需求 = (本期末库存 - 本期末积压)
            # I[p, q-1] - B[p, q-1] + P[p,q] - D[p,q] = I[p,q] - B[p,q]
            # 整理为： I[p,q-1] + P[p,q] + B[p,q] = D[p,q] + I[p,q] + B[p,q-1]
            # 这个形式更标准，表示 (可供量) + (新欠货) = (需求) + (结转库存) + (已满足的旧欠货或继续欠)

            backlog_at_start_of_quarter = B[p, q - 1] if q > 0 else 0  # 初始无积压

            model.addConstr(inventory_at_start_of_quarter + P[p, q] +
                            B[p, q] == demand[p, q] + I[p, q] +
                            backlog_at_start_of_quarter,
                            name=f"InventoryBalance_{p}_Q{q+1}")

    # 3. 特定生产限制: 产品I在第二季度 (索引1) 不能生产
    model.addConstr(
        P[production_restriction_product, production_restriction_quarter] == 0,
        name=
        f"NoProduction_{production_restriction_product}_Q{production_restriction_quarter+1}"
    )

    # 4. 期末库存要求: 第四季度末 (索引3)
    for p in products:
        model.addConstr(I[p, quarters[-1]] >= ending_inventory_target[p],
                        name=f"EndingInventory_{p}")
        # 确保第四季度末没有积压订单，虽然目标函数会尝试最小化积压，但这里可以明确要求
        # 如果允许第四季度末有积压，则不需要此约束。题目未明确禁止，但通常目标是清零。
        # 考虑到有期末库存目标，清零积压是合理的。
        model.addConstr(B[p, quarters[-1]] == 0, name=f"EndingBacklogZero_{p}")

    # --- 模型求解 ---
    model.optimize()

    # --- 打印结果 ---
    if model.status == GRB.OPTIMAL:
        print(f"\n找到最优生产计划! 最小总成本: {model.objVal:,.2f} 元")
        print("-" * 100)
        print(
            f"{'产品':<5} | {'季度':<5} | {'生产量':>10} | {'期末库存':>10} | {'期末积压':>10} | {'需求量':>10}"
        )
        print("=" * 100)
        for q in quarters:
            for p in products:
                print(
                    f"{p:<5} | {q+1:<5} | {P[p,q].X:>10.1f} | {I[p,q].X:>10.1f} | {B[p,q].X:>10.1f} | {demand[p,q]:>10}"
                )
            print("-" * 100)

        print("\n成本构成:")
        calc_total_backlog_cost = sum(
            B[p, q].X * backlog_cost_per_unit_per_quarter[p] for p in products
            for q in quarters)
        calc_total_inventory_cost = sum(
            I[p, q].X * inventory_cost_per_unit_per_quarter for p in products
            for q in quarters)
        print(f"  总延期赔偿成本: {calc_total_backlog_cost:,.2f} 元")
        print(f"  总库存持有成本: {calc_total_inventory_cost:,.2f} 元")
        print(
            f"  计算得到的总成本: {calc_total_backlog_cost + calc_total_inventory_cost:,.2f} 元"
        )

    elif model.status == GRB.INFEASIBLE:
        print("模型不可行。请检查约束条件是否相互冲突。")
        print("正在计算不可行子系统 (IIS) 来帮助定位问题...")
        model.computeIIS()
        model.write("factory_scheduling_iis.ilp")
        print("IIS 已写入 factory_scheduling_iis.ilp 文件。")
    elif model.status == GRB.UNBOUNDED:
        print("模型无界。目标函数可以无限减小。")
    else:
        print(f"优化过程因状态码 {model.status} 而停止。")


if __name__ == '__main__':
    solve_factory_scheduling()
