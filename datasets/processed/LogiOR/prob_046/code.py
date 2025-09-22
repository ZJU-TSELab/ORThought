import gurobipy as gp
from gurobipy import GRB


def solve_fund_allocation(
    initial_funds=50000.0,
    revenues={1: 20000.0, 2: 25000.0, 3: 30000.0, 4: 35000.0},
    expenses={1: 15000.0, 2: 35000.0, 3: 22000.0, 4: 28000.0},
    monthly_interest_rates={
        1: 0.002,
        2: 0.008,
        3: 0.015,
        4: 0.030
    }
):
    """
    Solves the SupplyChain Dynamics fund allocation problem.
    """
    try:
        # --- 1. Model Data ---
        months_invest = [1, 2, 3, 4]
        months_balance = [1, 2, 3, 4]
        investment_durations = [1, 2, 3, 4]

        # --- 2. Create Gurobi Model ---
        model = gp.Model("SupplyChainFundAllocation")
        model.Params.LogToConsole = 0

        # --- 3. Decision Variables ---
        X = model.addVars([(t, d) for t in months_invest for d in investment_durations if t + d <= 5],
                          name="InvestAmount", lb=0.0, vtype=GRB.CONTINUOUS)
        C = model.addVars(months_balance, name="CashOnHandEndOfMonth", lb=0.0, vtype=GRB.CONTINUOUS)

        # --- 4. Objective Function ---
        cash_at_month_5_start = C[4] + gp.quicksum(
            X[t, d] * (1 + d * monthly_interest_rates[d])
            for t in months_invest for d in investment_durations if (t, d) in X and t + d == 5)
        model.setObjective(cash_at_month_5_start, GRB.MAXIMIZE)

        # --- 5. Constraints ---
        for t in months_invest:
            if t == 1:
                funds_in = initial_funds + revenues[t] - expenses[t]
            else:
                cash_from_last_month = C[t - 1]
                maturing_investments_value = gp.quicksum(
                    X[t_invest, d_invest] * (1 + d_invest * monthly_interest_rates[d_invest])
                    for t_invest in months_invest for d_invest in investment_durations
                    if (t_invest, d_invest) in X and t_invest + d_invest == t)
                funds_in = cash_from_last_month + maturing_investments_value + revenues[t] - expenses[t]

            new_investments_made_this_month = gp.quicksum(X[t, d] for d in investment_durations if (t, d) in X)
            cash_carried_over = C[t]
            model.addConstr(funds_in == new_investments_made_this_month + cash_carried_over, name=f"CashBalance_Month{t}")
            if t == 1:
                model.addConstr(expenses[t] <= initial_funds + revenues[t], name=f"Expenses_Month{t}")
            else:
                model.addConstr(expenses[t] <= C[t - 1] + revenues[t], name=f"Expenses_Month{t}")

        # --- 6. Solve Model ---
        model.optimize()

        # --- 7. Return Results ---
        if model.Status == GRB.OPTIMAL:
            return {"status": "optimal", "obj": model.ObjVal}
        else:
            return {"status": f"{model.Status}"}

    except gp.GurobiError as e:
        return {"status": f"Gurobi error: {e}"}
    except Exception as e:
        return {"status": f"An unexpected error occurred: {e}"}


if __name__ == "__main__":
    result = solve_fund_allocation()
    print(result)
