import gurobipy as gp
from gurobipy import GRB


def optimize_lighting(min_total_fixtures=300,
                      max_electricity=2000,
                      led_electricity=5,
                      fluorescence_electricity=8,
                      led_changes=3,
                      fluorescence_changes=4,
                      fluorescence_ratio=0.3):
    # Create a new model
    m = gp.Model("LightingOptimization")

    # Decision variables: number of fixtures
    x_LED = m.addVar(vtype=GRB.INTEGER, lb=0, name="x_LED")
    x_F = m.addVar(vtype=GRB.INTEGER, lb=0, name="x_F")

    # Set objective: minimize total changes
    total_changes = led_changes * x_LED + fluorescence_changes * x_F
    m.setObjective(total_changes, GRB.MINIMIZE)

    # Add constraints
    # 1. Minimum total fixtures
    m.addConstr(x_LED + x_F >= min_total_fixtures, "MinFixtures")

    # 2. Electricity consumption limit
    m.addConstr(
        led_electricity * x_LED + fluorescence_electricity * x_F
        <= max_electricity, "ElectricityLimit")

    # 3. Fluorescence proportion constraint
    # x_F >= 0.3 * (x_LED + x_F)
    # Rearranged: 0.7 * x_F >= 0.3 * x_LED
    m.addConstr(0.7 * x_F >= 0.3 * x_LED, "FluorescenceRatio")

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        return m.objVal
    else:
        return None

# Example usage
if __name__ == "__main__":
    result = optimize_lighting()
    print(f"Optimal total changes: {result}")