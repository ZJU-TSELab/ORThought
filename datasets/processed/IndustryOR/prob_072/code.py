import gurobipy as gp
from gurobipy import GRB


def solve_child_selection():
    """
    Solves the Li family child selection problem to minimize cost
    subject to various constraints.
    """
    try:
        # --- Data ---
        children = ['Alice', 'Bob', 'Charlie', 'Diana', 'Ella']
        costs = {
            'Alice': 1000,
            'Bob': 900,
            'Charlie': 600,
            'Diana': 500,
            'Ella': 700
        }

        max_children_allowed = 3
        min_children_required = 2

        # --- Create Gurobi Model ---
        model = gp.Model("ChildSelection")

        # --- Decision Variables ---
        # x[c]: 1 if child c is taken, 0 otherwise
        x = model.addVars(children, vtype=GRB.BINARY, name="TakeChild")

        # --- Objective Function: Minimize Total Cost ---
        model.setObjective(gp.quicksum(costs[c] * x[c] for c in children),
                           GRB.MINIMIZE)

        # --- Constraints ---
        # 1. Max Children: Take up to 3 children
        model.addConstr(gp.quicksum(x[c] for c in children)
                        <= max_children_allowed,
                        name="MaxChildren")

        # 2. Must Take Bob
        model.addConstr(x['Bob'] == 1, name="MustTakeBob")

        # 3. Alice vs Diana: If Alice is taken, Diana is not (x_A + x_D <= 1)
        model.addConstr(x['Alice'] + x['Diana'] <= 1, name="Alice_vs_Diana")

        # 4. Bob vs Charlie: If Bob is taken, Charlie is not.
        # Since Bob must be taken (Constraint 2), this implies Charlie cannot be taken.
        model.addConstr(x['Charlie'] == 0, name="NoCharlie_due_to_Bob")
        # Original constraint: x['Charlie'] <= (1 - x['Bob']). Since x['Bob'] = 1, this becomes x['Charlie'] <= 0.

        # 5. Charlie implies Diana: If Charlie is taken, Diana must be taken (x_C <= x_D)
        # This constraint becomes redundant due to Constraint 4 (x_C = 0), but included for completeness.
        model.addConstr(x['Charlie'] <= x['Diana'],
                        name="Charlie_implies_Diana")

        # 6. Diana implies Ella: If Diana is taken, Ella must be taken (x_D <= x_E)
        model.addConstr(x['Diana'] <= x['Ella'], name="Diana_implies_Ella")

        # 7. Min Children: Take at least two children
        model.addConstr(gp.quicksum(x[c] for c in children)
                        >= min_children_required,
                        name="MinChildren")

        # Suppress Gurobi output to console if desired
        # model.setParam('OutputFlag', 0)

        # Optimize the model
        model.optimize()

        # --- Results ---
        if model.status == GRB.OPTIMAL:
            print("Optimal selection found.")
            print(f"Minimum Total Cost: ${model.ObjVal:.2f}")

            print("\nChildren to take:")
            selected_children = []
            for c in children:
                if x[c].X > 0.5:  # Check if x[c] is 1
                    selected_children.append(c)
                    print(f"  - {c} (Cost: ${costs[c]})")
            print(
                f"\nTotal number of children taken: {len(selected_children)}")

        elif model.status == GRB.INFEASIBLE:
            print(
                "Model is infeasible. The constraints cannot be satisfied simultaneously."
            )
            print("Please review the constraints:")
            print(f" - Max Children <= {max_children_allowed}")
            print(f" - Min Children >= {min_children_required}")
            print(f" - Must take Bob (Cost: ${costs['Bob']})")
            print(f" - Cannot take Charlie (due to Bob)")
            print(f" - If Alice taken, Diana not taken")
            print(f" - If Diana taken, Ella must be taken")
            # Compute and print IIS (Irreducible Inconsistent Subsystem)
            model.computeIIS()
            model.write("child_selection_iis.ilp")
            print("IIS written to child_selection_iis.ilp.")
        else:
            print(f"Optimization stopped with status: {model.status}")

    except gp.GurobiError as e:
        print(f"Gurobi error code {e.errno}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == '__main__':
    solve_child_selection()
