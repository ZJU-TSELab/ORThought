import gurobipy as gp
from gurobipy import GRB
import math


def solve_bomber_problem():
    try:
        # --- Parameters ---
        # Key Part | Distance (km) | P(Destroy | Heavy) | P(Destroy | Light)
        # 1        | 450           | 0.10             | 0.08
        # 2        | 480           | 0.20             | 0.16
        # 3        | 540           | 0.15             | 0.12
        # 4        | 600           | 0.25             | 0.20

        num_parts = 4
        parts = range(num_parts)

        distances = [450, 480, 540, 600]  # km
        prob_destroy_heavy = [0.10, 0.20, 0.15, 0.25]
        prob_destroy_light = [0.08, 0.16, 0.12, 0.20]

        # Resource Limits
        max_fuel = 48000  # liters
        max_heavy_bombs = 48
        max_light_bombs = 32

        # Fuel Consumption Parameters
        eff_heavy_loaded = 2.0  # km/liter
        eff_light_loaded = 3.0  # km/liter
        eff_empty_return = 4.0  # km/liter (return trip)
        fuel_takeoff_landing = 100  # liters per trip

        # --- Pre-calculations ---

        # Fuel per trip for each bomb type to each part
        fuel_per_heavy_trip = []
        for d in distances:
            # Fuel to target (loaded) + Fuel return (empty) + Takeoff/Landing
            fuel = (d / eff_heavy_loaded) + (
                d / eff_empty_return) + fuel_takeoff_landing
            fuel_per_heavy_trip.append(fuel)

        fuel_per_light_trip = []
        for d in distances:
            # Fuel to target (loaded) + Fuel return (empty) + Takeoff/Landing
            fuel = (d / eff_light_loaded) + (
                d / eff_empty_return) + fuel_takeoff_landing
            fuel_per_light_trip.append(fuel)

        # Objective function coefficients: log(P(not destroyed by one bomb))
        # log(1 - p) will be negative. We want to minimize this sum.
        log_prob_not_destroy_heavy = []
        for p in prob_destroy_heavy:
            if p < 1.0:  # Ensure p is not 1 to avoid log(0)
                log_prob_not_destroy_heavy.append(math.log(1 - p))
            else:  # Should not happen with given data, but good for robustness
                log_prob_not_destroy_heavy.append(
                    -float('inf'))  # Effectively forces use if possible

        log_prob_not_destroy_light = []
        for p in prob_destroy_light:
            if p < 1.0:
                log_prob_not_destroy_light.append(math.log(1 - p))
            else:
                log_prob_not_destroy_light.append(-float('inf'))

        # --- Model Initialization ---
        model = gp.Model("StrategicBomberPlanning")

        # --- Decision Variables ---
        # x_h[i]: number of heavy bombs assigned to part i
        x_h = model.addVars(num_parts,
                            vtype=GRB.INTEGER,
                            name="HeavyBombs",
                            lb=0)
        # x_l[i]: number of light bombs assigned to part i
        x_l = model.addVars(num_parts,
                            vtype=GRB.INTEGER,
                            name="LightBombs",
                            lb=0)

        # --- Objective Function ---
        # Minimize the sum of log probabilities of NOT destroying each part
        # This is equivalent to maximizing the probability of destroying at least one part
        objective = gp.quicksum(log_prob_not_destroy_heavy[i] * x_h[i] for i in parts) + \
                    gp.quicksum(log_prob_not_destroy_light[i] * x_l[i] for i in parts)
        model.setObjective(objective, GRB.MINIMIZE)

        # --- Constraints ---

        # 1. Total heavy bombs constraint
        model.addConstr(
            gp.quicksum(x_h[i] for i in parts) <= max_heavy_bombs,
            "MaxHeavyBombs")

        # 2. Total light bombs constraint
        model.addConstr(
            gp.quicksum(x_l[i] for i in parts) <= max_light_bombs,
            "MaxLightBombs")

        # 3. Total fuel consumption constraint
        total_fuel_consumed = gp.quicksum(fuel_per_heavy_trip[i] * x_h[i] for i in parts) + \
                              gp.quicksum(fuel_per_light_trip[i] * x_l[i] for i in parts)
        model.addConstr(total_fuel_consumed <= max_fuel, "MaxFuel")

        # --- Optimize Model ---
        model.optimize()

        # --- Output results ---
        print("-" * 30)
        if model.status == GRB.OPTIMAL:
            print("Optimal solution found!")
            print(
                f"Objective Value (sum of log-probabilities of non-destruction): {model.objVal:.4f}"
            )

            # Calculate overall probability of success
            # P_success = 1 - exp(model.objVal) because model.objVal = ln(Q_total)
            prob_success = 1 - math.exp(model.objVal)
            print(
                f"Maximized Probability of Destroying at least one Target: {prob_success:.4%}"
            )
            print("-" * 30)

            print("Bombing Plan:")
            total_h_bombs_used = 0
            total_l_bombs_used = 0
            actual_fuel_consumed = 0

            for i in parts:
                num_h = x_h[i].X
                num_l = x_l[i].X
                if num_h > 0.5 or num_l > 0.5:  # Check if any bombs assigned (due to float results)
                    print(f"  Key Part {i+1}:")
                    print(f"    Heavy Bombs: {num_h:.0f}")
                    print(f"    Light Bombs: {num_l:.0f}")
                total_h_bombs_used += num_h
                total_l_bombs_used += num_l
                actual_fuel_consumed += num_h * fuel_per_heavy_trip[
                    i] + num_l * fuel_per_light_trip[i]

            print("-" * 30)
            print("Resource Utilization:")
            print(
                f"  Total Heavy Bombs Used: {total_h_bombs_used:.0f} / {max_heavy_bombs}"
            )
            print(
                f"  Total Light Bombs Used: {total_l_bombs_used:.0f} / {max_light_bombs}"
            )
            print(
                f"  Total Fuel Consumed: {actual_fuel_consumed:.2f} / {max_fuel} liters"
            )

        elif model.status == GRB.INFEASIBLE:
            print(
                "Model is infeasible. No solution exists under the given constraints."
            )
        elif model.status == GRB.UNBOUNDED:
            print("Model is unbounded.")
        else:
            print(f"Optimization was stopped with status {model.status}")

    except gp.GurobiError as e:
        print(f"Error code {e.errno}: {e}")
    except AttributeError:
        print(
            "Gurobi or one of its components is not available. Make sure Gurobi is installed and licensed."
        )
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    solve_bomber_problem()
