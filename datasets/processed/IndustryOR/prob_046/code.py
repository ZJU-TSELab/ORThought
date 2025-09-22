import gurobipy as gp
from gurobipy import GRB


def solve_farm_optimization():
    """
    Solves the farm operation planning problem to maximize annual net income.
    """
    try:
        # --- Data ---
        # Resources
        total_land = 100  # hectares
        total_funds = 15000  # yuan
        labor_aw_available = 3500  # person-days Autumn/Winter
        labor_ss_available = 4000  # person-days Spring/Summer

        # External labor income (yuan/person-day)
        income_external_labor_aw = 1.8
        income_external_labor_ss = 2.1

        # Crop data: [Labor AW, Labor SS, Net Income/hectare]
        crop_data = {
            'Soybean': {
                'labor_aw': 20,
                'labor_ss': 50,
                'income': 175
            },
            'Corn': {
                'labor_aw': 35,
                'labor_ss': 75,
                'income': 300
            },
            'Wheat': {
                'labor_aw': 10,
                'labor_ss': 40,
                'income': 120
            }
        }
        crops = list(crop_data.keys())

        # Animal data
        # Dairy Cow
        cow_investment = 400  # yuan/cow
        cow_land_feed = 1.5  # hectares/cow
        cow_labor_aw = 100  # person-days/cow
        cow_labor_ss = 50  # person-days/cow
        cow_income = 400  # yuan/cow
        cow_max_capacity = 32

        # Chicken
        chicken_investment = 3  # yuan/chicken
        # chicken_land_feed = 0 (explicitly stated "does not use land")
        chicken_labor_aw = 0.6  # person-days/chicken
        chicken_labor_ss = 0.3  # person-days/chicken
        chicken_income = 2  # yuan/chicken
        chicken_max_capacity = 3000

        # --- Create Gurobi Model ---
        model = gp.Model("FarmOptimization")

        # --- Decision Variables ---
        # Crop cultivation (hectares)
        X = model.addVars(crops, name="X", lb=0.0, vtype=GRB.CONTINUOUS)

        # Number of animals (integer)
        N_cow = model.addVar(name="N_cow", lb=0.0, vtype=GRB.INTEGER)
        N_chicken = model.addVar(name="N_chicken", lb=0.0, vtype=GRB.INTEGER)

        # External labor sold (person-days)
        L_aw_out = model.addVar(name="L_aw_out", lb=0.0, vtype=GRB.CONTINUOUS)
        L_ss_out = model.addVar(name="L_ss_out", lb=0.0, vtype=GRB.CONTINUOUS)

        # --- Objective Function: Maximize Total Annual Net Income ---
        total_income = gp.quicksum(crop_data[c]['income'] * X[c] for c in crops) + \
                       cow_income * N_cow + \
                       chicken_income * N_chicken + \
                       income_external_labor_aw * L_aw_out + \
                       income_external_labor_ss * L_ss_out

        model.setObjective(total_income, GRB.MAXIMIZE)

        # --- Constraints ---
        # 1. Land Constraint
        land_for_cows = cow_land_feed * N_cow
        total_land_used = gp.quicksum(X[c] for c in crops) + land_for_cows
        model.addConstr(total_land_used <= total_land, name="LandLimit")

        # 2. Funds Constraint
        total_investment = cow_investment * N_cow + chicken_investment * N_chicken
        model.addConstr(total_investment <= total_funds, name="FundsLimit")

        # 3. Labor Constraint (Autumn/Winter)
        labor_aw_farm = gp.quicksum(crop_data[c]['labor_aw'] * X[c] for c in crops) + \
                        cow_labor_aw * N_cow + \
                        chicken_labor_aw * N_chicken
        model.addConstr(labor_aw_farm + L_aw_out <= labor_aw_available,
                        name="LaborAWLimit")

        # 4. Labor Constraint (Spring/Summer)
        labor_ss_farm = gp.quicksum(crop_data[c]['labor_ss'] * X[c] for c in crops) + \
                        cow_labor_ss * N_cow + \
                        chicken_labor_ss * N_chicken
        model.addConstr(labor_ss_farm + L_ss_out <= labor_ss_available,
                        name="LaborSSLimit")

        # 5. Animal Housing Capacity Constraints
        model.addConstr(N_cow <= cow_max_capacity, name="CowCapacity")
        model.addConstr(N_chicken <= chicken_max_capacity,
                        name="ChickenCapacity")

        # Suppress Gurobi output to console if desired
        # model.setParam('OutputFlag', 0)

        # Optimize the model
        model.optimize()

        # --- Results ---
        if model.status == GRB.OPTIMAL:
            print("Optimal farm operating plan found.")
            print(f"Maximum Annual Net Income: {model.ObjVal:.2f} Yuan")

            print("\nOptimal Plan Details:")
            print("  Crops (hectares):")
            for c in crops:
                if X[c].X > 1e-6:
                    print(f"    {c}: {X[c].X:.2f} ha")

            print("  Animals (number):")
            if N_cow.X > 1e-6:
                print(f"    Dairy Cows: {N_cow.X:.0f}")
            if N_chicken.X > 1e-6:
                print(f"    Chickens: {N_chicken.X:.0f}")

            print("  External Labor Sold (person-days):")
            if L_aw_out.X > 1e-6:
                print(
                    f"    Autumn/Winter: {L_aw_out.X:.2f} person-days (Income: {income_external_labor_aw * L_aw_out.X:.2f} Yuan)"
                )
            if L_ss_out.X > 1e-6:
                print(
                    f"    Spring/Summer: {L_ss_out.X:.2f} person-days (Income: {income_external_labor_ss * L_ss_out.X:.2f} Yuan)"
                )

            print("\nResource Utilization:")
            print(
                f"  Land Used: {total_land_used.getValue():.2f} / {total_land} ha ({(total_land_used.getValue()/total_land*100) if total_land > 0 else 0:.1f}%)"
            )
            print(
                f"  Funds Used: {total_investment.getValue():.2f} / {total_funds} Yuan ({(total_investment.getValue()/total_funds*100) if total_funds > 0 else 0:.1f}%)"
            )
            print(
                f"  Labor Autumn/Winter Used (Farm + External): {(labor_aw_farm.getValue() + L_aw_out.X):.2f} / {labor_aw_available} person-days (Farm: {labor_aw_farm.getValue():.2f}, External: {L_aw_out.X:.2f})"
            )
            print(
                f"  Labor Spring/Summer Used (Farm + External): {(labor_ss_farm.getValue() + L_ss_out.X):.2f} / {labor_ss_available} person-days (Farm: {labor_ss_farm.getValue():.2f}, External: {L_ss_out.X:.2f})"
            )
            print(f"  Cow Capacity Used: {N_cow.X:.0f} / {cow_max_capacity}")
            print(
                f"  Chicken Capacity Used: {N_chicken.X:.0f} / {chicken_max_capacity}"
            )

        elif model.status == GRB.INFEASIBLE:
            print("Model is infeasible. Check constraints and data.")
            # Compute and print IIS (Irreducible Inconsistent Subsystem)
            # model.computeIIS()
            # model.write("farm_optimization_iis.ilp")
            # print("IIS written to farm_optimization_iis.ilp")
        else:
            print(f"Optimization stopped with status: {model.status}")

    except gp.GurobiError as e:
        print(f"Gurobi error code {e.errno}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == '__main__':
    solve_farm_optimization()
