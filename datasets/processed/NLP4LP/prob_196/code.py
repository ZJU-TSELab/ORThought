def optimize_paper_production(
    profit_graph=4,
    profit_music=2.5,
    time_print_graph=3,
    time_scan_graph=5.5,
    time_print_music=1.5,
    time_scan_music=3,
    machine_time_limit=350
):
    import gurobipy as gp
    from gurobipy import GRB

    # Create a new model
    model = gp.Model("Paper_Production_Maximize_Profit")

    # Decision variables: number of reams of each product
    x = model.addVar(name="Graph_Paper", lb=0, vtype=GRB.INTEGER)
    y = model.addVar(name="Music_Paper", lb=0, vtype=GRB.INTEGER)

    # Set objective: maximize profit
    model.setObjective(profit_graph * x + profit_music * y, GRB.MAXIMIZE)

    # Add constraints
    # Printing machine constraint
    model.addConstr(time_print_graph * x + time_print_music * y <= machine_time_limit, "Printing_Time")
    # Scanning machine constraint
    model.addConstr(time_scan_graph * x + time_scan_music * y <= machine_time_limit, "Scanning_Time")

    # Optimize the model
    model.optimize()

    # Check if a feasible solution was found
    if model.status == GRB.OPTIMAL:
        # Return the maximum profit
        return model.objVal
    else:
        # No feasible solution found
        return None
# Example usage
if __name__ == "__main__":
    max_profit = optimize_paper_production()
    if max_profit is not None:
        print(f"Maximum Profit: ${max_profit}")
    else:
        print("No feasible solution found.")