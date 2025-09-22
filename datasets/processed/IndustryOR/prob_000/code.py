import gurobipy as gp
from gurobipy import GRB


def solve_factory_problem():
    model = gp.Model("FactoryProductionTraining")

    # --- Parameters ---
    weeks = range(1, 9)  # 1 to 8
    products = [1, 2]  # Food I and II

    initial_skilled_workers = 50
    new_workers_to_train_total = 50

    # Demand (kg)
    demand_data = {
        1: {
            1: 10000,
            2: 10000,
            3: 12000,
            4: 12000,
            5: 16000,
            6: 16000,
            7: 20000,
            8: 20000
        },
        2: {
            1: 6000,
            2: 7200,
            3: 8400,
            4: 10800,
            5: 10800,
            6: 12000,
            7: 12000,
            8: 12000
        }
    }

    # Production rates (kg/h per worker)
    prod_rate = {1: 10, 2: 6}

    # Work hours per week
    hours_normal = 40
    hours_overtime = 60

    # Wages (yuan per week)
    wage_skilled_normal = 360
    wage_skilled_overtime = 540
    wage_trainee = 120
    wage_newly_skilled = 240  # After training

    # Training: 1 skilled trains up to 3 new workers in 2 weeks
    training_ratio = 3  # new workers per skilled trainer
    training_duration = 2  # weeks

    # Compensation fee for delay (yuan per kg per week of delay)
    delay_penalty = {1: 0.5, 2: 0.6}

    initial_inventory = {
        1: 0,
        2: 0
    }  # Assuming no initial inventory or backlog

    # --- Decision Variables ---

    # Original skilled workers allocation
    sw_normal = model.addVars(weeks, name="SW_Normal", vtype=GRB.INTEGER, lb=0)
    sw_overtime = model.addVars(weeks,
                                name="SW_Overtime",
                                vtype=GRB.INTEGER,
                                lb=0)
    sw_train = model.addVars(weeks, name="SW_Train", vtype=GRB.INTEGER, lb=0)
    sw_train_start = model.addVars(weeks,
                                   name="SW_Train_Start",
                                   vtype=GRB.INTEGER,
                                   lb=0)
    # New workers
    nw_start_training = model.addVars(weeks,
                                      name="NW_Start_Training",
                                      vtype=GRB.INTEGER,
                                      lb=0)
    nw_training = model.addVars(weeks,
                                name="NW_Training",
                                vtype=GRB.INTEGER,
                                lb=0)  # Workers currently in training
    nw_newly_skilled_prod = model.addVars(weeks,
                                          name="NW_Newly_Skilled_Prod",
                                          vtype=GRB.INTEGER,
                                          lb=0)

    # Hours allocation by worker type and product
    h_sw_normal = model.addVars(weeks,
                                products,
                                name="H_SW_Normal",
                                vtype=GRB.CONTINUOUS,
                                lb=0)
    h_sw_overtime = model.addVars(weeks,
                                  products,
                                  name="H_SW_Overtime",
                                  vtype=GRB.CONTINUOUS,
                                  lb=0)
    h_nw_newly_skilled = model.addVars(weeks,
                                       products,
                                       name="H_NW_Newly_Skilled",
                                       vtype=GRB.CONTINUOUS,
                                       lb=0)

    # Production quantities
    P = model.addVars(weeks,
                      products,
                      name="Production",
                      vtype=GRB.CONTINUOUS,
                      lb=0)

    # Inventory and Backlog
    # The problem does not mention inventory, but considering that it may exist in real-world scenarios, we include this variable here with an initial value of 0. If needed, you can modify the upper bound of this variable.
    Inv = model.addVars(weeks,
                        products,
                        name="Inventory",
                        vtype=GRB.CONTINUOUS,
                        ub=0,
                        lb=0)
    Backlog_Surrogate = model.addVars(weeks,
                                      products,
                                      name="Backlog_Surrogate",
                                      vtype=GRB.CONTINUOUS,
                                      lb=0)

    # --- Objective Function: Minimize Total Cost ---
    total_cost = gp.LinExpr()

    for w in weeks:
        # Wages for original skilled workers
        total_cost += sw_normal[w] * wage_skilled_normal
        total_cost += sw_overtime[w] * wage_skilled_overtime
        total_cost += sw_train[w] * wage_skilled_normal

        # Wages for trainees
        total_cost += nw_training[w] * wage_trainee

        # Wages for newly skilled workers (once they complete training and start producing)
        total_cost += nw_newly_skilled_prod[w] * wage_newly_skilled

        # Penalties for backlog
        for p in products:
            total_cost += Backlog_Surrogate[w, p] * delay_penalty[p]

    model.setObjective(total_cost, GRB.MINIMIZE)

    # --- Constraints ---

    # C1: Original Skilled Worker Pool Allocation
    for w in weeks:
        model.addConstr(sw_normal[w] + sw_overtime[w] +
                        sw_train[w] == initial_skilled_workers,
                        name=f"OriginalSW_Allocation_w{w}")
        if w < training_duration:
            model.addConstr(sw_train[w] == sum(sw_train_start[w_inner]
                                               for w_inner in range(1, w + 1)),
                            name=f"SW_TrainStart_Accumulation_w{w}")
        else:
            model.addConstr(sw_train[w] == sum(sw_train_start[w_inner]
                                               for w_inner in range(w - training_duration + 1, w + 1)),
                            name=f"SW_TrainStart_Accumulation_w{w}")

    # C2: New Worker Training Target
    model.addConstr(
        gp.quicksum(nw_start_training[w] for w in range(1, 8)) ==
        new_workers_to_train_total,  # Weeks 1 to 7 for starting
        name="TotalNewWorkersTrained")
    model.addConstr(nw_start_training[8] == 0, name="NoTrainingStartInWeek8")
    for w in weeks:
        if w == 1:
            model.addConstr(nw_training[w] == nw_start_training[w],
                            name=f"NewWorkersTrainingStart_w{w}")
        else:
            model.addConstr(nw_training[w] == sum(nw_start_training[w_inner]
                                                   for w_inner in range(w - training_duration + 1, w + 1)),
                            name=f"NewWorkersTraining_w{w}")

    # C3: Newly Skilled Worker Availability for Production
    for w in weeks:
        if w <= training_duration:
            model.addConstr(nw_newly_skilled_prod[w] == 0,
                            name=f"NoNewlySkilled_w{w}")
        else:
            model.addConstr(nw_newly_skilled_prod[w] == nw_newly_skilled_prod[w-1] +
                            nw_start_training[w - training_duration],
                            name=f"NewlySkilledAvailability_w{w}")

    # C4: Training Capacity
    for w in weeks:
        model.addConstr(nw_start_training[w] <= training_ratio * sw_train_start[w],
                        name=f"TrainingCapacity_w{w}")

    # C5: Production Hours Allocation by Worker Type
    for w in weeks:
        # for p_idx, p_val in enumerate(
        #         products
        # ):  # Use p_val for keys, p_idx for list access if needed
        # Original skilled workers - normal time
        model.addConstr(gp.quicksum(h_sw_normal[w, p_inner]
                                    for p_inner in products)
                        == sw_normal[w] * hours_normal,
                        name=f"Hours_SW_Normal_Total_w{w}"
                        )  # Sum hours over products for this worker group
        # Original skilled workers - overtime
        model.addConstr(gp.quicksum(h_sw_overtime[w, p_inner]
                                    for p_inner in products)
                        == sw_overtime[w] * hours_overtime,
                        name=f"Hours_SW_Overtime_Total_w{w}")
        # Newly skilled workers - normal time
        model.addConstr(gp.quicksum(h_nw_newly_skilled[w, p_inner]
                                    for p_inner in products)
                        == nw_newly_skilled_prod[w] * hours_normal,
                        name=f"Hours_NW_NewlySkilled_Total_w{w}")
    # Correction for C5: The constraints should be for the sum of hours for *that worker group* not per product.
    # The above was trying to do it per product, fixed it to be per worker group total hours.

    # C6: Production Calculation
    for w in weeks:
        for p in products:
            total_hours_on_p = h_sw_normal[w, p] + h_sw_overtime[
                w, p] + h_nw_newly_skilled[w, p]
            model.addConstr(P[w, p] == total_hours_on_p * prod_rate[p],
                            name=f"ProductionCalc_w{w}_p{p}")

    # C7: Inventory Balance and Backlog Surrogate
    for p in products:
        for w in weeks:
            prev_inv = Inv[w - 1, p] if w > 1 else initial_inventory[p]
            model.addConstr(Inv[w, p] == prev_inv + P[w, p] - demand_data[p][w],
                            name=f"InventoryBalance_w{w}_p{p}")
            model.addConstr(Backlog_Surrogate[w, p] >= -Inv[w, p],
                            name=f"BacklogDef_w{w}_p{p}")
            # Backlog_Surrogate[w,p] >= 0 is already defined by lb=0 on the variable.
    model.addConstrs((Backlog_Surrogate[8, p] == 0 for p in products),
                     name="NoBacklogInWeek8")  # No backlog in week 8

    # --- Solve ---
    model.optimize()

    # --- Output Results ---
    if model.status == GRB.OPTIMAL:
        print(f"\nOptimal total cost: {model.ObjVal:.2f} yuan\n")

        # Summary of workers allocation
        print("--- Workers Allocation Summary ---")
        print(
            "Week | SW_Normal | SW_Overtime | SW_Train| NW_Training_Start | NW_Training | NW_Prod"
        )
        for w in weeks:
            print(
                f"{w:4} | {sw_normal[w].X:9.0f} | {sw_overtime[w].X:11.0f} | {sw_train[w].X:8.0f}| {nw_start_training[w].X:16.0f}  | {nw_training[w].X:11.0f} | {nw_newly_skilled_prod[w].X:7.0f}"
            )

        # Production and backlog summary for each product
        for p in products:
            print(f"\n--- Production & Backlog Summary (Food {p}) ---")
            print("Week | Demand | Produced | Inventory_End | Backlog | Backlog_Penalty")
            for w in weeks:
                backlog_penalty = Backlog_Surrogate[w, p].X * delay_penalty[p]
                print(f"{w:4} | {demand_data[p][w]:6} | {P[w, p].X:8.2f} | {Inv[w, p].X:14.2f} | {Backlog_Surrogate[w, p].X:7.2f} | {backlog_penalty:15.2f}")

    elif model.status == GRB.INFEASIBLE:
        print("Model is infeasible. Computing IIS to find conflicting constraints...")
        model.computeIIS()
        model.write("factory_model.ilp")  # Write the IIS to a file
        print("IIS written to factory_model.ilp. Please check this file to identify the cause of infeasibility.")
    else:
        print(f"Optimization ended with status: {model.status}")

    return model


if __name__ == '__main__':
    # Correcting the C5 constraint definition logic which was duplicated per product inside the loop.
    # It should be one constraint per worker group per week.

    # Create a temporary model instance to correct C5 structure before calling solve_factory_problem
    temp_model = gp.Model()
    weeks_param = range(1, 9)
    products_param = [1, 2]
    sw_normal_param = temp_model.addVars(
        weeks_param, name="SW_Normal_param")  # dummy for structure
    h_sw_normal_param = temp_model.addVars(weeks_param,
                                           products_param,
                                           name="H_SW_Normal_param")

    # Corrected C5 logic demonstration (this is conceptual, actual fix is in the main function)
    # for w_param in weeks_param:
    #     temp_model.addConstr(gp.quicksum(h_sw_normal_param[w_param, p_param] for p_param in products_param) <= sw_normal_param[w_param] * hours_normal,
    #                     name=f"Hours_SW_Normal_Total_w{w_param}")
    # This logic IS correctly implemented in the solve_factory_problem function. The loop for 'p_idx, p_val' in C5 was misleading in my thought process but the gurobipy quicksum over products for each worker group is the correct implementation.

    solved_model = solve_factory_problem()
