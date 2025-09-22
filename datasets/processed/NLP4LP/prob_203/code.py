import gurobipy as gp
from gurobipy import GRB


def optimize_bets(total_budget=100000, risk_limit=30000):
    # Create a new model
    m = gp.Model("BettingOptimization")

    # Decision variables
    x_b = m.addVar(name="x_b", lb=0)
    x_h = m.addVar(name="x_h", lb=0)
    x_s = m.addVar(name="x_s", lb=0)

    # Set the objective: maximize expected payout
    m.setObjective(0.6 * x_b + 0.375 * x_h + 0.09 * x_s, GRB.MAXIMIZE)

    # Add constraints
    # Total investment equals total budget
    m.addConstr(x_b + x_h + x_s == total_budget, name="TotalInvestment")

    # Risk constraint
    m.addConstr(0.5 * x_b + 0.25 * x_h + 0.10 * x_s <= risk_limit,
                name="RiskLimit")

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        return m.objVal
    else:
        return None
# Example usage
if __name__ == "__main__":
    max_payout = optimize_bets()
    if max_payout is not None:
        print(f"Maximum Expected Payout: {max_payout}")
    else:
        print("No feasible solution found.")