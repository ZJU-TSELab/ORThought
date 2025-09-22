import gurobipy as gp
from gurobipy import GRB


def solve_car_parking(max_length_per_side=None):
    """
    Solves the car parking assignment problem to minimize the maximum length
    occupied on either side of the street.

    Args:
        max_length_per_side (float, optional): Maximum allowed length on one side. 
                                                If None, no limit is applied. Defaults to None.
    """
    try:
        # --- Data ---
        car_lengths = {
            1: 4.0,
            2: 4.5,
            3: 5.0,
            4: 4.1,
            5: 2.4,
            6: 5.2,
            7: 3.7,
            8: 3.5,
            9: 3.2,
            10: 4.5,
            11: 2.3,
            12: 3.3,
            13: 3.8,
            14: 4.6,
            15: 3.0
        }
        cars = list(car_lengths.keys())
        sides = [1, 2]

        total_car_length = sum(car_lengths.values())
        print(f"Total length of all cars: {total_car_length:.2f} meters")

        # --- Create Gurobi Model ---
        model_name = "CarParkingAssignment"
        if max_length_per_side is not None:
            model_name += f"_Max{max_length_per_side}"
        model = gp.Model(model_name)

        # --- Decision Variables ---
        # x[i,s]: 1 if car i is parked on side s, 0 otherwise
        x = model.addVars(cars, sides, vtype=GRB.BINARY, name="x_assign")

        # L_max: Maximum length occupied on either side
        L_max = model.addVar(name="L_max", lb=0.0, vtype=GRB.CONTINUOUS)

        # --- Objective Function: Minimize L_max ---
        model.setObjective(L_max, GRB.MINIMIZE)

        # --- Constraints ---
        # 1. Assignment Constraint: Each car assigned to exactly one side
        for i in cars:
            model.addConstr(gp.quicksum(x[i, s] for s in sides) == 1,
                            name=f"AssignCar_{i}")

        # 2. Maximum Length Definition: L_max >= length on each side
        for s in sides:
            length_on_side_s = gp.quicksum(car_lengths[i] * x[i, s]
                                           for i in cars)
            model.addConstr(L_max >= length_on_side_s, name=f"MaxLen_Side_{s}")

        # 3. (Optional) Side Length Limit Constraint
        if max_length_per_side is not None:
            print(
                f"\nAdding constraint: Max length per side <= {max_length_per_side} meters"
            )
            for s in sides:
                length_on_side_s = gp.quicksum(car_lengths[i] * x[i, s]
                                               for i in cars)
                model.addConstr(length_on_side_s <= max_length_per_side,
                                name=f"SideLimit_{s}")

        # Suppress Gurobi output to console if desired
        # model.setParam('OutputFlag', 0)

        # Optimize the model
        model.optimize()

        # --- Results ---
        if model.status == GRB.OPTIMAL:
            print("\nOptimal parking assignment found.")
            print(
                f"Minimum Maximum Length Occupied (L_max): {model.ObjVal:.2f} meters"
            )

            print("\nParking Plan (Car -> Side):")
            assignment = {s: [] for s in sides}
            length_used = {s: 0.0 for s in sides}

            for i in cars:
                for s in sides:
                    if x[i, s].X > 0.5:  # Check if x[i,s] is 1
                        assignment[s].append(i)
                        length_used[s] += car_lengths[i]
                        break  # Move to next car

            for s in sides:
                print(f"  Side {s}: Cars {sorted(assignment[s])}")
                print(f"    -> Total Length: {length_used[s]:.2f} meters")
                if max_length_per_side is not None:
                    print(f"       (Limit: <= {max_length_per_side})")

        elif model.status == GRB.INFEASIBLE:
            print(
                "\nModel is infeasible. It's impossible to park the cars satisfying all constraints."
            )
            if max_length_per_side is not None:
                print(
                    f"  This might be due to the {max_length_per_side}m limit per side."
                )
                print(
                    f"  Total car length is {total_car_length:.2f}m, requiring at least {total_car_length/2:.2f}m per side on average."
                )
            # Compute and print IIS (Irreducible Inconsistent Subsystem)
            model.computeIIS()
            model.write("car_parking_iis.ilp")
            print("  IIS written to car_parking_iis.ilp for debugging.")
        else:
            print(f"\nOptimization stopped with status: {model.status}")
            if model.SolCount == 0:
                print("No feasible solution found.")

    except gp.GurobiError as e:
        print(f"Gurobi error code {e.errno}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


# --- Solve the problems ---
print("--- Scenario 1: Minimize Maximum Length (No Side Limit) ---")
solve_car_parking()

print("\n=========================================================\n")

print("--- Scenario 2: Minimize Maximum Length (Max 30m per Side) ---")
solve_car_parking(max_length_per_side=30.0)
