import gurobipy as gp
from gurobipy import GRB


def farmer_optimization(cow_price=500,
                        sheep_price=200,
                        chicken_price=8,
                        cow_feed_cost=100,
                        sheep_feed_cost=80,
                        chicken_feed_cost=5,
                        max_manure=800,
                        max_chickens=50,
                        min_cows=10,
                        min_sheep=20,
                        max_total_animals=100):
    """
    Solves the farmer's optimization problem to maximize profit given constraints on
    manure production, animal limits, and minimum required animals.

    Parameters:
        cow_price (float): Selling price for each cow. Default is 500.
        sheep_price (float): Selling price for each sheep. Default is 200.
        chicken_price (float): Selling price for each chicken. Default is 8.
        cow_feed_cost (float): Feed cost for each cow. Default is 100.
        sheep_feed_cost (float): Feed cost for each sheep. Default is 80.
        chicken_feed_cost (float): Feed cost for each chicken. Default is 5.
        max_manure (int): Maximum daily manure units allowed. Default is 800.
        max_chickens (int): Maximum number of chickens allowed. Default is 50.
        min_cows (int): Minimum number of cows required. Default is 10.
        min_sheep (int): Minimum number of sheep required. Default is 20.
        max_total_animals (int): Maximum total number of animals allowed. Default is 100.

    Returns:
        float or str: The optimal objective value if an optimal solution is found;
                      otherwise, returns the model status as a string.
    """
    model = gp.Model("Farmer_Optimization")
    model.setParam('OutputFlag', 0)  # Suppress output

    # Decision variables
    cows = model.addVar(vtype=GRB.INTEGER, name="cows")
    sheep = model.addVar(vtype=GRB.INTEGER, name="sheep")
    chickens = model.addVar(vtype=GRB.INTEGER, name="chickens")

    # Objective function
    profit_cow = cow_price - cow_feed_cost
    profit_sheep = sheep_price - sheep_feed_cost
    profit_chicken = chicken_price - chicken_feed_cost

    model.setObjective(profit_cow * cows + profit_sheep * sheep +
                       profit_chicken * chickens,
                       sense=GRB.MAXIMIZE)

    # Constraints
    model.addConstr(10 * cows + 5 * sheep + 3 * chickens <= max_manure,
                    "Manure_Capacity")
    model.addConstr(chickens <= max_chickens, "Max_Chickens")
    model.addConstr(cows >= min_cows, "Min_Cows")
    model.addConstr(sheep >= min_sheep, "Min_Sheep")
    model.addConstr(cows + sheep + chickens <= max_total_animals,
                    "Total_Animals")

    # Optimize
    model.optimize()

    if model.status == GRB.OPTIMAL:
        return model.ObjVal
    else:
        status_map = {
            GRB.INFEASIBLE: "Model is infeasible.",
            GRB.UNBOUNDED: "Model is unbounded.",
            GRB.SUBOPTIMAL: "Suboptimal solution found.",
            GRB.TIME_LIMIT: "Optimization stopped due to time limit.",
            GRB.INTERRUPTED: "Optimization interrupted."
        }
        return status_map.get(model.status,
                              f"Unknown status code {model.status}")
if __name__ == "__main__":
    result = farmer_optimization()
    print(f"Optimal profit: {result}")