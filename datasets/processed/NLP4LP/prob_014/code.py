def optimize_investment(total_budget=600000, max_apartment_investment=200000, apartment_return=0.10, townhouse_return=0.15):
    import gurobipy as gp
    from gurobipy import GRB

    # Create a new model
    model = gp.Model("RealEstateInvestment")

    # Decision variables
    x = model.addVar(name="Apartments", lb=0)  # Investment in apartments
    y = model.addVar(name="Townhouses", lb=0)  # Investment in townhouses

    # Set objective: maximize profit
    profit = apartment_return * x + townhouse_return * y
    model.setObjective(profit, GRB.MAXIMIZE)

    # Add constraints
    model.addConstr(x + y <= total_budget, name="TotalBudget")
    model.addConstr(x <= max_apartment_investment, name="ApartmentLimit")
    model.addConstr(x >= 0.5 * y, name="InvestmentRatio")

    # Optimize the model
    model.optimize()

    # Check if a feasible solution was found
    if model.status == GRB.OPTIMAL:
        # Return the maximum profit value
        return model.objVal
    else:
        # No feasible solution
        return None
# Example usage
if __name__ == "__main__":
    max_profit = optimize_investment()
    if max_profit is not None:
        print(f"Maximum Profit: {max_profit}")
    else:
        print("No feasible solution found.")