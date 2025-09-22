import gurobipy as gp
from gurobipy import GRB


def solve_investment_problem():
    """
    Solves the multi-period investment problem using Gurobi to maximize
    the total principal and interest at the end of the third year.
    """
    try:
        # Initial capital
        K0 = 300000.0

        # Create a new model
        model = gp.Model("MultiPeriodInvestment")

        # --- Decision Variables ---
        # x_ij: amount invested in project i at the start of year j
        # Project 1: Annual, 20% profit (return 1.2)
        x11 = model.addVar(name="x11_P1_Y1", lb=0.0,
                           vtype=GRB.CONTINUOUS)  # P1, Start of Year 1
        x12 = model.addVar(name="x12_P1_Y2", lb=0.0,
                           vtype=GRB.CONTINUOUS)  # P1, Start of Year 2
        x13 = model.addVar(name="x13_P1_Y3", lb=0.0,
                           vtype=GRB.CONTINUOUS)  # P1, Start of Year 3

        # Project 2: Start Y1, 2-year, 150% total return (factor 1.5), limit 150k
        x21 = model.addVar(name="x21_P2_Y1", lb=0.0, vtype=GRB.CONTINUOUS)

        # Project 3: Start Y2, 2-year, 160% total return (factor 1.6), limit 200k
        x32 = model.addVar(name="x32_P3_Y2", lb=0.0, vtype=GRB.CONTINUOUS)

        # Project 4: Start Y3, 1-year, 40% profit (return 1.4), limit 100k
        x43 = model.addVar(name="x43_P4_Y3", lb=0.0, vtype=GRB.CONTINUOUS)

        # --- Objective Function ---
        # Maximize total principal and interest at the end of Year 3.
        # Z = K0 + 0.2*x11 + 0.5*x21 + 0.2*x12 + 0.6*x32 + 0.2*x13 + 0.4*x43
        objective = K0 + 0.2 * x11 + 0.5 * x21 + 0.2 * x12 + 0.6 * x32 + 0.2 * x13 + 0.4 * x43
        model.setObjective(objective, GRB.MAXIMIZE)

        # --- Constraints ---
        # 1. Cash Availability at Start of Year 1
        model.addConstr(x11 + x21 <= K0, "Cash_SOY1")

        # 2. Cash Availability at Start of Year 2
        # Investments_SOY2 <= K0 + 0.2*x11 - x21
        # x12 + x32 - 0.2*x11 + x21 <= K0
        model.addConstr(x12 + x32 - 0.2 * x11 + x21 <= K0, "Cash_SOY2")

        # 3. Cash Availability at Start of Year 3
        # Investments_SOY3 <= K0 + 0.2*x11 + 0.5*x21 + 0.2*x12 - x32
        # x13 + x43 - 0.2*x11 - 0.5*x21 - 0.2*x12 + x32 <= K0
        model.addConstr(
            x13 + x43 - 0.2 * x11 - 0.5 * x21 - 0.2 * x12 + x32 <= K0,
            "Cash_SOY3")

        # 4. Investment Limit for Project 2
        model.addConstr(x21 <= 150000, "Limit_P2")

        # 5. Investment Limit for Project 3
        model.addConstr(x32 <= 200000, "Limit_P3")

        # 6. Investment Limit for Project 4
        model.addConstr(x43 <= 100000, "Limit_P4")

        # Suppress Gurobi output to console
        # model.setParam('OutputFlag', 0)

        # Optimize the model
        model.optimize()

        # --- Results ---
        if model.status == GRB.OPTIMAL:
            print("Optimal investment plan found.")
            print(
                f"Maximum Principal and Interest at End of Year 3: {model.objVal:.2f} yuan"
            )

            total_profit = model.objVal - K0
            print(f"Total Profit over 3 years: {total_profit:.2f} yuan")

            print("\nInvestment Plan Details (yuan):")
            print("  Start of Year 1:")
            print(f"    Project 1 (Annual, 20% profit): {x11.X:.2f}")
            print(
                f"    Project 2 (2-year, 150% return, limit 150k): {x21.X:.2f}"
            )
            cash_soy1_invested = x11.X + x21.X
            cash_soy1_uninvested = K0 - cash_soy1_invested
            print(f"    Total invested at SOY1: {cash_soy1_invested:.2f}")
            print(f"    Uninvested cash from SOY1: {cash_soy1_uninvested:.2f}")

            cash_available_soy2 = K0 + 0.2 * x11.X - x21.X
            print(
                f"\n  Cash available at Start of Year 2: {cash_available_soy2:.2f}"
            )
            print("  Start of Year 2:")
            print(f"    Project 1 (Annual, 20% profit): {x12.X:.2f}")
            print(
                f"    Project 3 (2-year, 160% return, limit 200k): {x32.X:.2f}"
            )
            cash_soy2_invested = x12.X + x32.X
            cash_soy2_uninvested = cash_available_soy2 - cash_soy2_invested
            print(f"    Total invested at SOY2: {cash_soy2_invested:.2f}")
            print(f"    Uninvested cash from SOY2: {cash_soy2_uninvested:.2f}")

            cash_available_soy3 = K0 + 0.2 * x11.X + 0.5 * x21.X + 0.2 * x12.X - x32.X
            print(
                f"\n  Cash available at Start of Year 3: {cash_available_soy3:.2f}"
            )
            print("  Start of Year 3:")
            print(f"    Project 1 (Annual, 20% profit): {x13.X:.2f}")
            print(
                f"    Project 4 (1-year, 40% profit, limit 100k): {x43.X:.2f}")
            cash_soy3_invested = x13.X + x43.X
            cash_soy3_uninvested = cash_available_soy3 - cash_soy3_invested
            print(f"    Total invested at SOY3: {cash_soy3_invested:.2f}")
            print(
                f"    Uninvested cash from SOY3 (carried to EOY3): {cash_soy3_uninvested:.2f}"
            )

        else:
            print("No optimal solution found. Status code:", model.status)

    except gp.GurobiError as e:
        print(f"Error code {e.errno}: {e}")
    except AttributeError:
        print(
            "Encountered an attribute error. Gurobi might not be installed or licensed correctly."
        )
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == '__main__':
    solve_investment_problem()
