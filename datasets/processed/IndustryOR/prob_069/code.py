import gurobipy as gp
from gurobipy import GRB


def solve_tsp_mtz():
    """
    Solves the Traveling Salesman Problem (TSP) for 4 cities
    using the Miller-Tucker-Zemlin (MTZ) formulation for subtour elimination.
    The objective is to minimize the total travel distance.
    """
    try:
        # --- Data ---
        # Number of cities
        num_cities = 4
        cities = range(num_cities)  # Indices 0, 1, 2, 3

        # Distance matrix d[i][j] is distance from city i to city j.
        # Mapping: City 1 -> 0, City 2 -> 1, City 3 -> 2, City 4 -> 3
        # Original Table:
        # | City |  1  |  2  |  3  |  4  |
        # | ---- | --- | --- | --- | --- |
        # | 1    | 0   | 10  | 20  | 12  |
        # | 2    | 10  | 0   | 5   | 10  |
        # | 3    | 20  | 5   | 0   | 8   |
        # | 4    | 15  | 12  | 8   | 0   |

        # Distances (costs) between cities. d[i][j] is cost from i to j.
        # Using a dictionary for clarity with non-sequential/sparse connections if any.
        # For a full matrix, a list of lists is also fine.
        distances = {
            (0, 1): 10,
            (0, 2): 20,
            (0, 3): 12,  # From City 1 (index 0)
            (1, 0): 10,
            (1, 2): 5,
            (1, 3): 10,  # From City 2 (index 1)
            (2, 0): 20,
            (2, 1): 5,
            (2, 3): 8,  # From City 3 (index 2)
            (3, 0): 15,
            (3, 1): 12,
            (3, 2): 8  # From City 4 (index 3)
        }
        # Note: d[i,i] is implicitly infinity or such arcs are excluded.

        # --- Create Gurobi Model ---
        model = gp.Model("TSP_MTZ")

        # --- Decision Variables ---
        # x[i,j]: 1 if salesman travels from city i to city j, 0 otherwise
        x = model.addVars(cities, cities, vtype=GRB.BINARY, name="x")

        # u[i]: auxiliary variable for MTZ subtour elimination (position of city i in tour)
        # u[0] will be fixed to 0 (or 1). Let's use 1 for positions 1 to N.
        u = model.addVars(cities,
                          vtype=GRB.CONTINUOUS,
                          name="u",
                          lb=1.0,
                          ub=num_cities)

        # --- Preprocessing: Remove x[i,i] variables (travel from a city to itself) ---
        for i in cities:
            x[i, i].ub = 0

        # --- Objective Function: Minimize Total Travel Distance ---
        model.setObjective(
            gp.quicksum(
                distances.get((i, j), 0) * x[i, j] for i in cities
                for j in cities if i != j), GRB.MINIMIZE)

        # --- Constraints ---
        # 1. Depart from each city exactly once
        for i in cities:
            model.addConstr(gp.quicksum(x[i, j] for j in cities
                                        if j != i) == 1,
                            name=f"DepartOnce_{i}")

        # 2. Enter each city exactly once
        for j in cities:
            model.addConstr(gp.quicksum(x[i, j] for i in cities
                                        if i != j) == 1,
                            name=f"EnterOnce_{j}")

        # 3. Subtour Elimination (MTZ constraints)
        # Let city 0 be the "depot" for sequencing purposes.
        model.addConstr(
            u[0] == 1,
            name="FixDepotOrder")  # Fix position of depot city (index 0)

        for i in cities:
            if i == 0:
                continue  # Skip depot for these u bounds if u[0] is fixed differently
            model.addConstr(u[i] >= 2,
                            name=f"u_lower_bound_{i}")  # Positions 2 to N
            model.addConstr(u[i] <= num_cities, name=f"u_upper_bound_{i}")

        for i in cities:
            for j in cities:
                if i == j or j == 0:  # Constraint is typically for non-depot j
                    continue
                # If x[i,j] = 1, then u[j] >= u[i] + 1
                # u[i] - u[j] + num_cities * x[i,j] <= num_cities - 1
                model.addConstr(u[i] - u[j] + num_cities * x[i, j]
                                <= num_cities - 1,
                                name=f"MTZ_{i}_{j}")

        # Suppress Gurobi output to console if desired
        # model.setParam('OutputFlag', 0)

        # Optimize the model
        model.optimize()

        # --- Results ---
        if model.status == GRB.OPTIMAL:
            print("Optimal TSP route found.")
            print(f"Minimum Total Distance: {model.ObjVal:.2f}")

            print("\nOptimal Route (Original City Numbers):")
            # Reconstruct the path
            current_city_idx = 0  # Start from city 0 (Original City 1)
            route = [current_city_idx + 1]  # Store original city numbers

            for _ in range(num_cities - 1):
                found_next = False
                for j in cities:
                    if j != current_city_idx and x[current_city_idx,
                                                   j].X > 0.5:
                        route.append(j + 1)
                        current_city_idx = j
                        found_next = True
                        break
                if not found_next:
                    print("Error: Could not reconstruct full route.")
                    break

            if len(
                    route
            ) == num_cities:  # and current_city_idx is now the last city before returning to start
                # Check if it returns to start
                if x[current_city_idx, 0].X > 0.5:
                    route.append(route[0])  # Add starting city to show cycle
                    print(" -> ".join(map(str, route)))
                else:
                    print(
                        "Error: Route does not return to start or is incomplete."
                    )
                    print("Partial route:", " -> ".join(map(str, route)))
            else:
                print("Error: Route reconstruction failed or incomplete.")
                print("Partial route:", " -> ".join(map(str, route)))

            print("\nSequence variables u_i (Original City Numbers):")
            for i in cities:
                print(f"  City {i+1}: u = {u[i].X:.1f}")

            print("\nArcs used (Original City Numbers):")
            for i in cities:
                for j in cities:
                    if i != j and x[i, j].X > 0.5:
                        print(
                            f"  {i+1} -> {j+1} (Distance: {distances.get((i,j),0)})"
                        )

        elif model.status == GRB.INFEASIBLE:
            print("Model is infeasible. Check constraints and data.")
            # Compute and print IIS (Irreducible Inconsistent Subsystem)
            # model.computeIIS()
            # model.write("tsp_mtz_iis.ilp")
            # print("IIS written to tsp_mtz_iis.ilp.")
        else:
            print(f"Optimization stopped with status: {model.status}")

    except gp.GurobiError as e:
        print(f"Gurobi error code {e.errno}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == '__main__':
    solve_tsp_mtz()
