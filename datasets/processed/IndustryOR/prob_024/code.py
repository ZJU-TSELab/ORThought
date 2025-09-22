import gurobipy as gp
from gurobipy import GRB


def solve_investment_problem():
    """
    Solves the multi-period investment problem using Gurobi.
    """
    try:
        # --- Parameters ---
        K = 100000.0

        # --- Model Initialization ---
        model = gp.Model("InvestmentStrategy")

        # --- Decision Variables ---
        # x_ij: amount invested in option i at the start of year j (0-indexed for time)
        # Option 1: 1-year term, 1 yuan becomes 1.7 yuan (0.7 profit)
        # Option 2: 2-year term, 1 yuan becomes 3 yuan (2 profit)

        # Investments at Start of Year 1 (Time 0)
        x10 = model.addVar(name="x10", lb=0.0,
                           vtype=GRB.CONTINUOUS)  # Opt1, Year 1
        x20 = model.addVar(name="x20", lb=0.0,
                           vtype=GRB.CONTINUOUS)  # Opt2, Year 1 (matures EOY2)

        # Investments at Start of Year 2 (Time 1)
        x11 = model.addVar(name="x11", lb=0.0,
                           vtype=GRB.CONTINUOUS)  # Opt1, Year 2
        x21 = model.addVar(name="x21", lb=0.0,
                           vtype=GRB.CONTINUOUS)  # Opt2, Year 2 (matures EOY3)

        # Investments at Start of Year 3 (Time 2)
        x12 = model.addVar(name="x12", lb=0.0,
                           vtype=GRB.CONTINUOUS)  # Opt1, Year 3
        # No x22 as Opt2 takes 2 years and goal is EOY3

        # --- Objective Function ---
        # Maximize total earnings by the end of year 3.
        # Earnings = (Total value at EOY3) - K
        # Total value = K + 0.7*x10 + 2*x20 + 0.7*x11 + 2*x21 + 0.7*x12
        # Earnings = 0.7*x10 + 2*x20 + 0.7*x11 + 2*x21 + 0.7*x12
        objective = 0.7 * x10 + 2.0 * x20 + 0.7 * x11 + 2.0 * x21 + 0.7 * x12
        model.setObjective(objective, GRB.MAXIMIZE)

        # --- Constraints ---
        # Constraint 1: Cash availability at Start of Year 1 (Time 0)
        model.addConstr(x10 + x20 <= K, "Cash_Year1_Start")

        # Constraint 2: Cash availability at Start of Year 2 (Time 1)
        # Money available = (K - x10 - x20) (uninvested T0) + 1.7*x10 (from x10 maturing)
        # x11 + x21 <= K + 0.7*x10 - x20
        model.addConstr(x11 + x21 - 0.7 * x10 + x20 <= K, "Cash_Year2_Start")

        # Constraint 3: Cash availability at Start of Year 3 (Time 2)
        # Money available at T2 = (Cash_Available_T1 - x11 - x21) (uninvested T1)
        #                         + 1.7*x11 (from x11 maturing)
        #                         + 3.0*x20 (from x20 maturing)
        # Cash_Available_T1 = K + 0.7*x10 - x20
        # Money available at T2 = (K + 0.7*x10 - x20 - x11 - x21) + 1.7*x11 + 3.0*x20
        #                       = K + 0.7*x10 + 2.0*x20 + 0.7*x11 - x21
        # x12 <= K + 0.7*x10 + 2.0*x20 + 0.7*x11 - x21
        model.addConstr(x12 - 0.7 * x10 - 2.0 * x20 - 0.7 * x11 + x21 <= K,
                        "Cash_Year3_Start")

        # Suppress Gurobi output to console
        model.setParam('OutputFlag', 0)

        # Optimize the model
        model.optimize()

        # --- Results ---
        if model.status == GRB.OPTIMAL:
            print("Optimal solution found.")
            print(f"Maximum Earnings: {model.objVal:.2f} yuan")
            print("\nInvestment Plan:")
            print(f"  Start of Year 1 (Time 0):")
            print(f"    Invest in Option 1 (x10): {x10.X:.2f} yuan")
            print(f"    Invest in Option 2 (x20): {x20.X:.2f} yuan")

            available_t1 = K - x10.X - x20.X + 1.7 * x10.X
            print(
                f"\n  Cash available at Start of Year 2 (Time 1): {available_t1:.2f} yuan"
            )
            print(f"  Start of Year 2 (Time 1):")
            print(f"    Invest in Option 1 (x11): {x11.X:.2f} yuan")
            print(f"    Invest in Option 2 (x21): {x21.X:.2f} yuan")

            available_t2 = available_t1 - x11.X - x21.X + 1.7 * x11.X + 3.0 * x20.X
            print(
                f"\n  Cash available at Start of Year 3 (Time 2): {available_t2:.2f} yuan"
            )
            print(f"  Start of Year 3 (Time 2):")
            print(f"    Invest in Option 1 (x12): {x12.X:.2f} yuan")

            total_value_eoy3 = K + model.objVal
            print(
                f"\nTotal value at End of Year 3: {total_value_eoy3:.2f} yuan")

        else:
            print("No optimal solution found. Status code:", model.status)

    except gp.GurobiError as e:
        print(f"Error code {e.errno}: {e}")
    except AttributeError:
        print(
            "Encountered an attribute error, Gurobi might not be installed or licensed correctly."
        )


if __name__ == '__main__':
    solve_investment_problem()
