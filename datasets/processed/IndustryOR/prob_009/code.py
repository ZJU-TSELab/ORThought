from gurobipy import Model, GRB, quicksum


def solve_supermarket_location():
    # --- 模型初始化 ---
    model = Model("SupermarketSetCovering")

    # --- 集合定义 ---
    # 住宅区既是潜在的建店地点，也是需要被覆盖的区域
    locations = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L"]
    areas_to_cover = locations[:]  # 创建一个副本

    # --- 参数定义 ---
    # coverage_data[loc] 是一个列表，包含地点loc建店可以覆盖的所有区域
    coverage_data = {
        "A": ["A", "C", "E", "G", "H", "I"],
        "B": ["B", "H", "I"],
        "C": ["A", "C", "G", "H", "I"],
        "D": ["D", "J"],
        "E": ["A", "E", "G"],
        "F": ["F", "J", "K"],
        "G": ["A", "C", "E", "G"],
        "H": ["A", "B", "C", "H", "I"],
        "I": ["A", "B", "C", "H", "I"],
        "J": ["D", "F", "J", "K", "L"],
        "K": ["F", "J", "K", "L"],
        "L": ["J", "K", "L"],
    }

    # --- 决策变量 ---
    # build[loc]: 是否在地点loc建店 (1=是, 0=否)
    build = model.addVars(locations, name="BuildStore", vtype=GRB.BINARY)

    # --- 目标函数: 最小化建店数量 ---
    model.setObjective(quicksum(build[loc] for loc in locations), GRB.MINIMIZE)

    # --- 约束条件: 每个区域至少被一个店覆盖 ---
    for area in areas_to_cover:
        # 找出哪些潜在店址可以覆盖当前区域 area
        covering_locations = []
        for loc_candidate in locations:
            if area in coverage_data[loc_candidate]:
                covering_locations.append(loc_candidate)

        # 添加约束: sum(build[loc] for loc in covering_locations) >= 1
        if covering_locations:  # 确保列表不为空，尽管在此问题中每个区域都至少能被自己覆盖
            model.addConstr(quicksum(build[loc] for loc in covering_locations)
                            >= 1,
                            name=f"CoverArea_{area}")
        else:
            print(f"警告: 区域 {area} 无法被任何潜在店址覆盖。请检查数据。")

    # --- 模型求解 ---
    model.optimize()

    # --- 打印结果 ---
    if model.status == GRB.OPTIMAL:
        print(f"\n找到最优选址方案! 最少建店数量: {model.objVal:.0f}")
        print("建店地点:")
        for loc in locations:
            if build[loc].X > 0.5:  # 检查二元变量是否为1
                print(f"  - 在区域 {loc} 建店")

        print("\n各区域覆盖情况:")
        for area in areas_to_cover:
            covered_by_stores = []
            for loc in locations:
                if build[loc].X > 0.5 and area in coverage_data[loc]:
                    covered_by_stores.append(loc)
            print(
                f"  区域 {area} 被以下店址覆盖: {', '.join(covered_by_stores) if covered_by_stores else '未被覆盖 (错误!)'}"
            )

    elif model.status == GRB.INFEASIBLE:
        print("模型不可行。请检查约束条件或覆盖数据。")
        print("可能原因：某个区域无法被任何潜在店址覆盖。")
    elif model.status == GRB.UNBOUNDED:
        print("模型无界。(在此问题中不应发生)")
    else:
        print(f"优化过程因状态码 {model.status} 而停止。")


if __name__ == '__main__':
    solve_supermarket_location()
