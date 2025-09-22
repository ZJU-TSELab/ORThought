import gurobipy as gp
from gurobipy import GRB


def solve_pharma_distribution_corrected(
    T=range(1, 7),
    P=['P1', 'P2'],
    D=['DC1', 'DC2', 'DC3'],
    R=['R1', 'R2', 'R3', 'R4'],
    B=range(-1, 7),
    L=2,
    BigM_flow=2400,
    Demand={
        ('R1', 1): 100,
        ('R1', 2): 110,
        ('R1', 3): 120,
        ('R1', 4): 130,
        ('R1', 5): 140,
        ('R1', 6): 150,
        ('R2', 1): 80,
        ('R2', 2): 85,
        ('R2', 3): 90,
        ('R2', 4): 95,
        ('R2', 5): 100,
        ('R2', 6): 105,
        ('R3', 1): 120,
        ('R3', 2): 125,
        ('R3', 3): 130,
        ('R3', 4): 135,
        ('R3', 5): 140,
        ('R3', 6): 145,
        ('R4', 1): 60,
        ('R4', 2): 65,
        ('R4', 3): 70,
        ('R4', 4): 75,
        ('R4', 5): 80,
        ('R4', 6): 85
    },
    ProdCap={
        ('P1', 1): 250,
        ('P1', 2): 250,
        ('P1', 3): 260,
        ('P1', 4): 260,
        ('P1', 5): 270,
        ('P1', 6): 270,
        ('P2', 1): 200,
        ('P2', 2): 200,
        ('P2', 3): 210,
        ('P2', 4): 210,
        ('P2', 5): 220,
        ('P2', 6): 220
    },
    FixedDCost={'DC1': 10000, 'DC2': 12000, 'DC3': 9000},
    DCStoreCap={'DC1': 300, 'DC2': 350, 'DC3': 280},
    TransCostPD={
        ('P1', 'DC1'): 5,
        ('P1', 'DC2'): 7,
        ('P1', 'DC3'): 6,
        ('P2', 'DC1'): 8,
        ('P2', 'DC2'): 4,
        ('P2', 'DC3'): 7
    },
    TransCostDR={
        ('DC1', 'R1'): 3,
        ('DC1', 'R2'): 4,
        ('DC1', 'R3'): 5,
        ('DC1', 'R4'): 6,
        ('DC2', 'R1'): 5,
        ('DC2', 'R2'): 3,
        ('DC2', 'R3'): 4,
        ('DC2', 'R4'): 5,
        ('DC3', 'R1'): 4,
        ('DC3', 'R2'): 5,
        ('DC3', 'R3'): 3,
        ('DC3', 'R4'): 4
    },
    InvHoldCost={'DC1': 2.0, 'DC2': 2.5, 'DC3': 1.8},
    DisposalCost={'DC1': 1, 'DC2': 1, 'DC3': 1},
    ShortageCost={'R1': 50, 'R2': 50, 'R3': 50, 'R4': 50},
    InitialInv={('DC1', -1): 5, ('DC1', 0): 10}
):
    """
    Solves a corrected and robust version of the PharmaLogistics distribution network problem,
    accurately handling inventory flow and shelf life.
    """
    model = gp.Model("PharmaLogistics_Corrected")

    # ========== Decision Variables ==========
    Y = model.addVars(D, T, vtype=GRB.BINARY, name="Y_dc_open")
    P_prod = model.addVars(P, T, lb=0, name="P_prod")
    Q_ship_pd = model.addVars(P, D, T, lb=0, name="Q_ship_plant_dc")
    S_ship_dr = model.addVars(B, D, R, T, lb=0, name="S_ship_dc_region")
    I_inv = model.addVars(B, D, T, lb=0, name="I_inventory")
    U_unmet = model.addVars(R, T, lb=0, name="U_unmet_demand")
    W_waste = model.addVars(B, D, T, lb=0, name="W_waste")

    # ========== Objective Function ==========
    total_fixed_cost = gp.quicksum(FixedDCost[d] * Y[d, t] for d in D
                                   for t in T)
    total_transport_pd_cost = gp.quicksum(
        TransCostPD[p, d] * Q_ship_pd[p, d, t] for p in P for d in D
        for t in T)
    total_transport_dr_cost = gp.quicksum(
        TransCostDR[d, r] * S_ship_dr[b, d, r, t] for b in B for d in D
        for r in R for t in T)
    total_inventory_cost = gp.quicksum(InvHoldCost[d] * I_inv[b, d, t]
                                       for b in B for d in D for t in T)
    total_disposal_cost = gp.quicksum(DisposalCost[d] * W_waste[b, d, t]
                                      for b in B for d in D for t in T)
    total_shortage_cost = gp.quicksum(ShortageCost[r] * U_unmet[r, t]
                                      for r in R for t in T)

    model.setObjective(
        total_fixed_cost + total_transport_pd_cost +
        total_transport_dr_cost + total_inventory_cost +
        total_disposal_cost + total_shortage_cost, GRB.MINIMIZE)

    # ========== Constraints ==========
    # DC Activation and Capacity
    model.addConstrs((gp.quicksum(I_inv[b, d, t]
                                  for b in B) <= DCStoreCap[d] * Y[d, t]
                      for d in D for t in T),
                     name="DC_Capacity")
    model.addConstrs((gp.quicksum(Q_ship_pd[p, d, t]
                                  for p in P) <= BigM_flow * Y[d, t]
                      for d in D for t in T),
                     name="DC_Open_Inbound")
    model.addConstrs((gp.quicksum(S_ship_dr[b, d, r, t] for b in B
                                  for r in R) <= BigM_flow * Y[d, t]
                      for d in D for t in T),
                     name="DC_Open_Outbound")

    # Production and Plant Flow
    model.addConstrs((P_prod[p, t] <= ProdCap[p, t] for p in P for t in T),
                     name="Production_Capacity")
    model.addConstrs((P_prod[p, t] == gp.quicksum(Q_ship_pd[p, d, t]
                                                  for d in D) for p in P
                      for t in T),
                     name="Plant_Flow")

    # Inventory Balance and Shelf Life
    for d in D:
        for t in T:
            for b in B:
                # Previous inventory
                if t == 1:
                    prev_inv = InitialInv.get((d, b), 0)
                else:
                    prev_inv = I_inv[b, d, t - 1]

                # Inflow from production
                inflow = gp.quicksum(Q_ship_pd[p, d, t]
                                     for p in P) if b == t else 0

                # Outflow to customers
                outflow = gp.quicksum(S_ship_dr[b, d, r, t] for r in R)

                # Inventory Balance Equation
                model.addConstr(I_inv[b, d, t] == prev_inv + inflow -
                                outflow - W_waste[b, d, t],
                                name=f"Inv_Balance_{b}_{d}_{t}")

                # --- CORRECTED: Shelf-life constraints ---
                # Product from batch 'b' expires at the end of period 'b + L - 1'
                expiration_period = b + L - 1

                # If the current period 't' is after the expiration period, inventory must be zero
                if t > expiration_period:
                    model.addConstr(I_inv[b, d, t] == 0,
                                    f"Expired_Inv_Zero_{b}_{d}_{t}")

                # Waste can only occur AT the expiration period.
                if t == expiration_period:
                    # Waste is whatever is left from the previous period that isn't shipped out
                    model.addConstr(W_waste[b, d, t] == prev_inv - outflow,
                                    f"Waste_Calc_{b}_{d}_{t}")
                else:
                    model.addConstr(W_waste[b, d, t] == 0,
                                    f"No_Waste_{b}_{d}_{t}")

    # Demand Satisfaction
    for r in R:
        for t in T:
            # Sum of shipments from all DCs and all VALID (non-expired) batches
            valid_shipments = gp.quicksum(S_ship_dr[b, d, r, t] for d in D
                                          for b in B if t < b + L)
            model.addConstr(valid_shipments + U_unmet[r, t] == Demand[r,
                                                                      t],
                            name=f"Demand_{r}_{t}")

    # ========== Solve ==========
    model.Params.TimeLimit = 120  # 2-minute time limit for this complex model
    model.optimize()

    # ========== Return Results ==========
    if model.Status == GRB.OPTIMAL or model.Status == GRB.TIME_LIMIT:
        return {"status": "optimal", "obj": model.ObjVal}
    else:
        return {"status": f"{model.Status}"}


if __name__ == "__main__":
    result = solve_pharma_distribution_corrected()
    print(result)
