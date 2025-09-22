def optimize_amusement_park():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("AmusementPark")

    # Decision variables
    T = m.addVar(name="ThrowingGames", vtype=GRB.INTEGER, lb=0)
    C = m.addVar(name="ClimbingGames", vtype=GRB.INTEGER, lb=0)

    # Set objective: maximize total customers
    m.setObjective(15 * T + 8 * C, GRB.MAXIMIZE)

    # Add constraints
    m.addConstr(2 * T + 3 * C <= 100, name="PrizeLimit")
    m.addConstr(T >= 2 * C, name="ThrowingAtLeastTwiceClimbing")
    m.addConstr(C >= 5, name="MinimumClimbing")
    
    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the maximum number of customers attracted
        return m.objVal
    else:
        # No feasible solution
        return None
# Example usage
if __name__ == "__main__":
    max_customers = optimize_amusement_park()
    if max_customers is not None:
        print(f"Maximum Customers Attracted: {max_customers}")
    else:
        print("No feasible solution found.")