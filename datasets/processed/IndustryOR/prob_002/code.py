from gurobipy import Model, GRB, quicksum
# import gurobipy # This line is redundant and has been removed


def solve_production_planning_revised():
    # --- Model Initialization ---
    # --- 模型初始化 ---
    m = Model("FoldableTableProductionRevised")

    # --- Time Horizon ---
    # --- 时间范围 ---
    months = list(range(6))
    month_names = ["January", "February", "March", "April", "May",
                   "June"]  # 月份名称

    # --- Parameters ---
    # --- 参数 ---
    raw_material_cost_per_unit = 90  # 原材料成本/单位 (元)
    regular_hourly_wage = 30  # 正常时薪 (元)
    overtime_hourly_wage = 40  # 加班时薪 (元)
    inventory_cost_per_unit_per_month = 15  # 库存成本/单位/月 (元)
    stockout_penalty_per_unmet_unit = 35  # 最终未满足需求的缺货成本/单位 (元)
    outsourcing_cost_per_unit = 200  # 外包成本/单位 (元)
    hiring_cost_per_worker = 5000  # 雇佣成本/人 (元)
    firing_cost_per_worker = 8000  # 解雇成本/人 (元)

    labor_hours_per_unit = 5  # 单位产品所需工时 (小时)
    selling_price_per_unit = 300  # 单位产品售价 (元)

    initial_workers = 1000  # 初始工人数
    normal_daily_working_hours = 8  # 每日正常工作时长 (小时)
    working_days_per_month = 20  # 每月工作天数
    normal_hours_per_worker_per_month = normal_daily_working_hours * working_days_per_month  # 每人每月正常工作时长 (小时)
    max_overtime_hours_per_worker_per_month = 20  # 每人每月最大加班时长 (小时)

    initial_inventory = 15000  # 初始库存 (单位)
    min_ending_inventory_june = 10000  # 六月底最低期末库存 (单位)

    # Demand Forecast (units per month)
    # 需求预测 (单位/月)
    demand_forecast = {
        0: 20000,  # January  (一月)
        1: 40000,  # February (二月)
        2: 42000,  # March    (三月)
        3: 35000,  # April    (四月)
        4: 19000,  # May      (五月)
        5: 18500  # June     (六月)
    }

    # --- Decision Variables ---
    # --- 决策变量 ---
    # P[t]: Production quantity in month t
    # P[t]: 月份 t 的生产数量
    P = m.addVars(months, name="Production", vtype=GRB.INTEGER, lb=0)
    # W[t]: Number of workers during month t (after hiring/firing)
    # W[t]: 月份 t 的工人数 (雇佣/解雇后)
    W = m.addVars(months, name="Workers", vtype=GRB.INTEGER, lb=0)
    # H[t]: Number of workers hired at the start of month t
    # H[t]: 月份 t 初雇佣的工人数
    H = m.addVars(months, name="Hired", vtype=GRB.INTEGER, lb=0)
    # F[t]: Number of workers fired at the start of month t
    # F[t]: 月份 t 初解雇的工人数
    F = m.addVars(months, name="Fired", vtype=GRB.INTEGER, lb=0)
    # OT_total[t]: Total overtime hours in month t
    # OT_total[t]: 月份 t 的总加班工时
    OT_total = m.addVars(months, name="OvertimeHours", vtype=GRB.INTEGER, lb=0)
    # Inv[t]: Inventory at the end of month t
    # Inv[t]: 月份 t 的期末库存
    Inv = m.addVars(months, name="Inventory", vtype=GRB.INTEGER, lb=0)
    # Outsource[t]: Units outsourced in month t
    # Outsource[t]: 月份 t 的外包数量
    Outsource = m.addVars(months, name="Outsourced", vtype=GRB.INTEGER, lb=0)
    # S[t]: Final unmet demand (stockout) in month t
    # S[t]: 月份 t 的最终未满足需求 (缺货) 数量
    S = m.addVars(months, name="StockoutUnmet", vtype=GRB.INTEGER, lb=0)

    # --- Objective Function: Maximize Total Net Profit ---
    # --- 目标函数: 最大化总净利润 ---
    # Revenue is based on units sold (Demand - Unmet Stockout)
    # 收入基于销售数量 (需求 - 未满足的缺货)
    total_revenue = quicksum(
        (demand_forecast[t] - S[t]) * selling_price_per_unit for t in months)

    total_raw_material_cost = quicksum(P[t] * raw_material_cost_per_unit
                                       for t in months)
    total_regular_labor_cost = quicksum(
        W[t] * normal_hours_per_worker_per_month * regular_hourly_wage
        for t in months)
    total_overtime_labor_cost = quicksum(OT_total[t] * overtime_hourly_wage
                                         for t in months)
    total_inventory_cost = quicksum(Inv[t] * inventory_cost_per_unit_per_month
                                    for t in months)
    # Outsourcing cost is now separate
    # 外包成本现在是分开的
    total_outsourcing_cost = quicksum(Outsource[t] * outsourcing_cost_per_unit
                                      for t in months)
    # Stockout cost for final unmet demand
    # 最终未满足需求的缺货成本
    total_stockout_unmet_cost = quicksum(S[t] * stockout_penalty_per_unmet_unit
                                         for t in months)
    total_hiring_cost = quicksum(H[t] * hiring_cost_per_worker for t in months)
    total_firing_cost = quicksum(F[t] * firing_cost_per_worker for t in months)

    total_costs = (
        total_raw_material_cost + total_regular_labor_cost +
        total_overtime_labor_cost + total_inventory_cost +
        total_outsourcing_cost + total_stockout_unmet_cost
        +  # Added stockout cost for S[t] # 为S[t]添加了缺货成本
        total_hiring_cost + total_firing_cost)

    m.setObjective(total_revenue - total_costs, GRB.MAXIMIZE)

    # --- Constraints ---
    # --- 约束条件 ---
    for t in months:
        # 1. Worker Balance Constraint
        # 1. 工人数量平衡约束
        if t == 0:
            m.addConstr(W[t] == initial_workers + H[t] - F[t],
                        name=f"WorkerBalance_Month{t}")
        else:
            m.addConstr(W[t] == W[t - 1] + H[t] - F[t],
                        name=f"WorkerBalance_Month{t}")

        # 2. Production Labor Hours Constraint
        # 2. 生产工时约束
        m.addConstr(P[t] * labor_hours_per_unit
                    <= (W[t] * normal_hours_per_worker_per_month) +
                    OT_total[t],
                    name=f"ProductionCapacity_Month{t}")

        # 3. Overtime Limit Constraint
        # 3. 加班上限约束
        m.addConstr(OT_total[t]
                    <= W[t] * max_overtime_hours_per_worker_per_month,
                    name=f"OvertimeLimit_Month{t}")

        # 4. Inventory Balance Constraint
        # 4. 库存平衡约束
        # Inv[t] = Previous_Inv + P[t] + Outsource[t] - (Demand[t] - S[t])
        # This means: Ending_Inv + Sold_Units = Starting_Inv + Produced_Units + Outsourced_Units
        # 这意味着: 期末库存 + 销售数量 = 期初库存 + 生产数量 + 外包数量
        sold_units_t = demand_forecast[t] - S[t]
        if t == 0:
            m.addConstr(Inv[t] == initial_inventory + P[t] + Outsource[t] -
                        sold_units_t,
                        name=f"InventoryBalance_Month{t}")
        else:
            m.addConstr(Inv[t] == Inv[t - 1] + P[t] + Outsource[t] -
                        sold_units_t,
                        name=f"InventoryBalance_Month{t}")

        # 5. Stockout (Unmet Demand) Definition Constraints (Linearized max function)
        # 5. 缺货 (未满足需求) 定义约束 (线性化的max函数)
        # S[t] >= Demand[t] - Previous_Inv - P[t] - Outsource[t]
        # S[t] >= 0 (handled by lb=0 on variable S) (通过变量S的lb=0处理)
        if t == 0:
            m.addConstr(S[t] >= demand_forecast[t] - initial_inventory - P[t] -
                        Outsource[t],
                        name=f"StockoutDef_Month{t}")
        else:
            m.addConstr(S[t] >= demand_forecast[t] - Inv[t - 1] - P[t] -
                        Outsource[t],
                        name=f"StockoutDef_Month{t}")

    # 6. Minimum Ending Inventory Constraint (for June - month 5)
    # 6. 最低期末库存约束 (六月份 - 月份5)
    m.addConstr(Inv[months[-1]] >= min_ending_inventory_june,
                name="MinEndingInventory")

    # --- Solve Model ---
    # --- 求解模型 ---
    m.optimize()

    # --- Print Results ---
    # --- 打印结果 ---
    if m.status == GRB.OPTIMAL:
        print(
            f"\nOptimal Solution Found. Total Net Profit: {m.objVal:,.2f} Yuan"
        )
        print("-" * 60)
        print("Monthly Plan:")
        print("-" * 60)
        header = (
            f"{'Month':<10} | {'Demand':>8} | {'Sold':>8} | {'Unmet (S)':>9} | {'Workers':>7} | {'Hired':>6} | {'Fired':>6} | "
            f"{'Production':>10} | {'Outsourced':>10} | {'OvertimeH':>10} | {'Avg OT/W':>8} | {'End Inv':>10}"
        )
        print(header)
        print("=" * len(header))

        total_prod = 0
        total_outs = 0
        total_hired = 0
        total_fired = 0
        total_ot = 0
        total_unmet_s = 0
        total_sold = 0

        for t in months:
            workers_t = W[t].X
            avg_ot_per_worker = (OT_total[t].X /
                                 workers_t) if workers_t > 0 else 0
            sold_t = demand_forecast[t] - S[t].X
            total_sold += sold_t
            total_unmet_s += S[t].X
            print(
                f"{month_names[t]:<10} | {demand_forecast[t]:>8,.0f} | {sold_t:>8,.0f} | {S[t].X:>9,.2f} | "
                f"{workers_t:>7,.0f} | {H[t].X:>6,.0f} | {F[t].X:>6,.0f} | "
                f"{P[t].X:>10,.2f} | {Outsource[t].X:>10,.2f} | {OT_total[t].X:>10,.2f} | "
                f"{avg_ot_per_worker:>8,.2f} | {Inv[t].X:>10,.2f}")
            total_prod += P[t].X
            total_outs += Outsource[t].X
            total_hired += H[t].X
            total_fired += F[t].X
            total_ot += OT_total[t].X

        print("=" * len(header))
        print("Summary over 6 months:")
        print(f"Total Demand: {sum(demand_forecast.values()):,.0f} units")
        print(f"Total Sold: {total_sold:,.0f} units")
        print(f"Total Unmet Demand (S): {total_unmet_s:,.2f} units")
        print(f"Total Production: {total_prod:,.2f} units")
        print(f"Total Outsourced: {total_outs:,.2f} units")
        print(f"Total Hired: {total_hired:,.0f} workers")
        print(f"Total Fired: {total_fired:,.0f} workers")
        print(f"Total Overtime Hours: {total_ot:,.2f} hours")
        print(
            f"Ending Inventory (June): {Inv[months[-1]].X:,.2f} units (Min required: {min_ending_inventory_june:,})"
        )
        print("-" * 60)

        # Recalculate costs and revenue for verification
        # 重新计算成本和收入以进行验证
        calc_revenue = sum(
            (demand_forecast[t] - S[t].X) * selling_price_per_unit
            for t in months)
        calc_rm_cost = sum(P[t].X * raw_material_cost_per_unit for t in months)
        calc_reg_labor_cost = sum(W[t].X * normal_hours_per_worker_per_month *
                                  regular_hourly_wage for t in months)
        calc_ot_labor_cost = sum(OT_total[t].X * overtime_hourly_wage
                                 for t in months)
        calc_inv_cost = sum(Inv[t].X * inventory_cost_per_unit_per_month
                            for t in months)
        calc_outs_cost = sum(Outsource[t].X * outsourcing_cost_per_unit
                             for t in months)
        calc_stockout_unmet_cost = sum(S[t].X * stockout_penalty_per_unmet_unit
                                       for t in months)
        calc_hir_cost = sum(H[t].X * hiring_cost_per_worker for t in months)
        calc_fir_cost = sum(F[t].X * firing_cost_per_worker for t in months)
        calc_total_costs = calc_rm_cost + calc_reg_labor_cost + calc_ot_labor_cost + calc_inv_cost + calc_outs_cost + calc_stockout_unmet_cost + calc_hir_cost + calc_fir_cost

        print(
            "\nBreakdown of Total Revenue and Costs (Calculated from solution):"
        )
        print(f"  Total Revenue (from sold units): {calc_revenue:,.2f} Yuan")
        print(f"  Total Raw Material Cost: {calc_rm_cost:,.2f} Yuan")
        print(f"  Total Regular Labor Cost: {calc_reg_labor_cost:,.2f} Yuan")
        print(f"  Total Overtime Labor Cost: {calc_ot_labor_cost:,.2f} Yuan")
        print(f"  Total Inventory Cost: {calc_inv_cost:,.2f} Yuan")
        print(f"  Total Outsourcing Cost (base): {calc_outs_cost:,.2f} Yuan")
        print(
            f"  Total Stockout Unmet Cost (for S>0): {calc_stockout_unmet_cost:,.2f} Yuan"
        )
        print(f"  Total Hiring Cost: {calc_hir_cost:,.2f} Yuan")
        print(f"  Total Firing Cost: {calc_fir_cost:,.2f} Yuan")
        print(f"  Calculated Total Costs: {calc_total_costs:,.2f} Yuan")
        print(
            f"  Calculated Net Profit (Revenue - Costs): {calc_revenue - calc_total_costs:,.2f} Yuan (Should match Gurobi's m.objVal)"
        )

    elif m.status == GRB.INFEASIBLE:
        print("Model is infeasible. Check constraints.")  # 模型不可行，请检查约束
        m.computeIIS()
        m.write("model_revised_iis.ilp")
        print("IIS written to model_revised_iis.ilp"
              )  # IIS已写入model_revised_iis.ilp
    elif m.status == GRB.UNBOUNDED:
        print("Model is unbounded.")  # 模型无界
    else:
        print(
            f"Optimization was stopped with status {m.status}")  # 优化已停止，状态为...


if __name__ == '__main__':
    solve_production_planning_revised()
