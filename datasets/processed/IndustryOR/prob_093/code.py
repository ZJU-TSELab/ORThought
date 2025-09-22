from gurobipy import Model, GRB, quicksum

# 创建模型
model = Model("Crude_Oil_Blending_Improved")

# ----------------------------
# 参数设置
# ----------------------------
price_I = 4800  # Type I 汽油售价
price_II = 5600  # Type II 汽油售价

cost_A_segment1 = 10000  # 第一段成本（前500吨）
cost_A_segment2 = 8000  # 第二段成本（500~1000吨）
cost_A_segment3 = 6000  # 第三段成本（超过1000吨）

max_segment1 = 500  # 第一段最大购买量
max_segment2 = 500  # 第二段最大购买量
max_segment3 = 500  # 第三段最大购买量（总共最多1500）

inv_A = 500  # 现有原油A库存
inv_B = 1000  # 现有原油B库存

M = 1e6  # 大M值

# ----------------------------
# 决策变量
# ----------------------------

# 汽油产量
x1 = model.addVar(name="Gasoline_TypeI")
x2 = model.addVar(name="Gasoline_TypeII")

# 原油使用量
a1 = model.addVar(name="CrudeA_TypeI")
b1 = model.addVar(name="CrudeB_TypeI")
a2 = model.addVar(name="CrudeA_TypeII")
b2 = model.addVar(name="CrudeB_TypeII")

# 购买的原油 A 分段数量
pa1 = model.addVar(ub=max_segment1, name="PurchaseA_Segment1")  # ≤500
pa2 = model.addVar(ub=max_segment2, name="PurchaseA_Segment2")  # ≤500
pa3 = model.addVar(ub=max_segment3, name="PurchaseA_Segment3")  # ≤500

# 是否进入某分段的二元变量
y1 = model.addVar(vtype=GRB.BINARY, name="Segment1_Active")
y2 = model.addVar(vtype=GRB.BINARY, name="Segment2_Active")
y3 = model.addVar(vtype=GRB.BINARY, name="Segment3_Active")

# 总共使用的原油A和B
total_a_used = a1 + a2
total_b_used = b1 + b2

# ----------------------------
# 约束条件
# ----------------------------

# 1. 汽油生产由对应原油组成
model.addConstr(a1 + b1 == x1, "TypeI_Production")
model.addConstr(a2 + b2 == x2, "TypeII_Production")

# 2. 原油A占比约束
model.addConstr(a1 >= 0.5 * x1, "TypeI_Min_A_Content")
model.addConstr(a2 >= 0.6 * x2, "TypeII_Min_A_Content")

# 3. 原油使用总量不能超过库存+购买量
model.addConstr(total_a_used <= inv_A + pa1 + pa2 + pa3, "CrudeA_Limit")
model.addConstr(total_b_used <= inv_B, "CrudeB_Limit")

# 4. 分段购买逻辑约束（必须买满前面段才允许进入下一段）
# 第一段：只要 y1=1，就可以买，但不超过 max_segment1
model.addConstr(pa1 <= max_segment1 * y1, "Segment1_Upper")
model.addConstr(pa1 >= 0)

# 第二段：只能在 y2=1 且 pa1 已买满时才能购买
model.addConstr(pa2 <= max_segment2 * y2, "Segment2_Upper")
model.addConstr(y1 >= y2, "Must_Fill_Segment1_First")
model.addConstr(pa1 >= max_segment1 * y2, "Fill_Segment1_Before_Segment2")

# 第三段：只能在 y3=1 且 pa1、pa2 都已买满时才能购买
model.addConstr(pa3 <= max_segment3 * y3, "Segment3_Upper")
model.addConstr(y2 >= y3, "Must_Fill_Segment2_Before_Segment3")
# model.addConstr(pa1 >= max_segment1 * y3, "Fill_Segment1_Before_Segment3")
model.addConstr(pa2 >= max_segment2 * y3, "Fill_Segment2_Before_Segment3")

# ----------------------------
# 目标函数：最大化利润 = 销售收入 - 原油成本
# ----------------------------

revenue = price_I * x1 + price_II * x2
purchase_cost = cost_A_segment1 * pa1 + cost_A_segment2 * pa2 + cost_A_segment3 * pa3

profit = revenue - purchase_cost

model.setObjective(profit, GRB.MAXIMIZE)

# ----------------------------
# 求解模型
# ----------------------------

model.optimize()

# ----------------------------
# 输出结果
# ----------------------------

if model.status == GRB.OPTIMAL:
    print("\nOptimal Solution Found:")
    print(f"Produce {x1.X:.2f} tons of Gasoline Type I")
    print(f"Produce {x2.X:.2f} tons of Gasoline Type II")
    print(f"Use {a1.X:.2f} tons of Crude A for Type I")
    print(f"Use {b1.X:.2f} tons of Crude B for Type I")
    print(f"Use {a2.X:.2f} tons of Crude A for Type II")
    print(f"Use {b2.X:.2f} tons of Crude B for Type II")
    print(f"Purchase Segment 1: {pa1.X:.2f} tons (<=500)")
    print(f"Purchase Segment 2: {pa2.X:.2f} tons (500~1000)")
    print(f"Purchase Segment 3: {pa3.X:.2f} tons (>1000)")
    print(f"Total Profit: {profit.getValue():.2f} yuan")
else:
    print("No optimal solution found.")
