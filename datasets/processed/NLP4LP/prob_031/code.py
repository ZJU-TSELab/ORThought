import gurobipy as gp
from gurobipy import GRB


def optimize_farm_operation(cost_old=300,
                            cost_new=200,
                            harvest_old={
                                'raspberries': 2,
                                'blueberries': 2,
                                'strawberries': 4
                            },
                            harvest_new={
                                'raspberries': 4,
                                'blueberries': 1,
                                'strawberries': 2
                            },
                            demand={
                                'raspberries': 10,
                                'blueberries': 9,
                                'strawberries': 15
                            },
                            max_time=300):
    # Create a new model
    m = gp.Model("FarmOptimization")
    m.setParam('TimeLimit', max_time)

    # Decision variables: number of days to operate each farm
    x_old = m.addVar(name="x_old", lb=0)
    x_new = m.addVar(name="x_new", lb=0)

    # Set objective: minimize total cost
    m.setObjective(cost_old * x_old + cost_new * x_new, GRB.MINIMIZE)

    # Add constraints for each fruit
    m.addConstr(harvest_old['raspberries'] * x_old +
                harvest_new['raspberries'] * x_new >= demand['raspberries'],
                name="Raspberries")
    m.addConstr(harvest_old['blueberries'] * x_old +
                harvest_new['blueberries'] * x_new >= demand['blueberries'],
                name="Blueberries")
    m.addConstr(harvest_old['strawberries'] * x_old +
                harvest_new['strawberries'] * x_new >= demand['strawberries'],
                name="Strawberries")

    # Optimize the model
    m.optimize()

    # Return the optimal total cost if found
    if m.status == GRB.OPTIMAL or m.status == GRB.TIME_LIMIT:
        return m.objVal
    else:
        return None

# Example usage
if __name__ == "__main__":
    min_cost = optimize_farm_operation()
    if min_cost is not None:
        print(f"Minimum Cost of Farm Operation: {min_cost}")
    else:
        print("No feasible solution found.")