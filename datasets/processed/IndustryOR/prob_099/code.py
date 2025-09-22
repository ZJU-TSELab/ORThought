import gurobipy as gp
from gurobipy import GRB


def solve_max_bandwidth_path():
    """
    Solves the problem of finding a path from node A to E via node C
    that maximizes the bottleneck bandwidth.
    """
    try:
        # --- Data ---
        nodes_map = {'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4}
        nodes_rev_map = {v: k for k, v in nodes_map.items()}
        num_nodes = len(nodes_map)
        all_nodes = range(num_nodes)

        start_node = nodes_map['A']
        intermediate_node = nodes_map['C']
        end_node = nodes_map['E']

        # Bandwidth matrix BW[i][j]
        #       A   B   C   D   E
        bw_data = [
            [0, 90, 85, 0, 65],  # A
            [95, 0, 70, 65, 34],  # B
            [60, 0, 0, 88, 80],  # C
            [67, 30, 25, 0, 84],  # D
            [0, 51, 0, 56, 0]  # E
        ]

        max_possible_bandwidth = 0
        for row in bw_data:
            for val in row:
                if val > max_possible_bandwidth:
                    max_possible_bandwidth = val
        if max_possible_bandwidth == 0:  # Should not happen with given data
            max_possible_bandwidth = 1000  # A large number

        # --- Create Gurobi Model ---
        model = gp.Model("MaxBandwidthPathViaC")

        # --- Decision Variables ---
        # x[i,j]: 1 if link (i,j) is in path A to C
        x = model.addVars(all_nodes,
                          all_nodes,
                          vtype=GRB.BINARY,
                          name="x_path_AC")
        # y[i,j]: 1 if link (i,j) is in path C to E
        y = model.addVars(all_nodes,
                          all_nodes,
                          vtype=GRB.BINARY,
                          name="y_path_CE")

        # B_overall: Overall bottleneck bandwidth of the A-C-E path
        B_overall = model.addVar(name="OverallBandwidth",
                                 lb=0.0,
                                 vtype=GRB.CONTINUOUS)

        # Remove self-loops and links with zero bandwidth
        for i in all_nodes:
            x[i, i].UB = 0
            y[i, i].UB = 0
            for j in all_nodes:
                if i == j: continue
                if bw_data[i][j] == 0:
                    x[i, j].UB = 0
                    y[i, j].UB = 0

        # --- Objective Function: Maximize B_overall ---
        model.setObjective(B_overall, GRB.MAXIMIZE)

        # --- Constraints ---
        # Path A (start_node) to C (intermediate_node) using x_vars
        # 1. Flow out of start_node A for path x
        model.addConstr(
            gp.quicksum(x[start_node, j] for j in all_nodes
                        if j != start_node) == 1, "FlowOut_A_x")
        # 2. No flow into start_node A for path x
        model.addConstr(
            gp.quicksum(x[j, start_node] for j in all_nodes
                        if j != start_node) == 0, "FlowIn_A_x")
        # 3. Flow into intermediate_node C for path x
        model.addConstr(
            gp.quicksum(x[i, intermediate_node] for i in all_nodes
                        if i != intermediate_node) == 1, "FlowIn_C_x")
        # 4. No flow out of intermediate_node C for path x
        model.addConstr(
            gp.quicksum(x[intermediate_node, j] for j in all_nodes
                        if j != intermediate_node) == 0, "FlowOut_C_x")
        # 5. Flow conservation for other nodes in path x
        for k in all_nodes:
            if k != start_node and k != intermediate_node:
                model.addConstr(gp.quicksum(x[i, k] for i in all_nodes
                                            if i != k) == gp.quicksum(
                                                x[k, j] for j in all_nodes
                                                if j != k),
                                name=f"FlowCons_x_{k}")
                # Ensure intermediate nodes are visited at most once
                model.addConstr(
                    gp.quicksum(x[i, k] for i in all_nodes if i != k) <= 1,
                    f"VisitOnce_x_{k}")

        # Path C (intermediate_node) to E (end_node) using y_vars
        # 6. Flow out of intermediate_node C for path y
        model.addConstr(
            gp.quicksum(y[intermediate_node, j] for j in all_nodes
                        if j != intermediate_node) == 1, "FlowOut_C_y")
        # 7. No flow into intermediate_node C for path y
        model.addConstr(
            gp.quicksum(y[j, intermediate_node] for j in all_nodes
                        if j != intermediate_node) == 0, "FlowIn_C_y")
        # 8. Flow into end_node E for path y
        model.addConstr(
            gp.quicksum(y[i, end_node] for i in all_nodes
                        if i != end_node) == 1, "FlowIn_E_y")
        # 9. No flow out of end_node E for path y
        model.addConstr(
            gp.quicksum(y[end_node, j] for j in all_nodes
                        if j != end_node) == 0, "FlowOut_E_y")
        # 10. Flow conservation for other nodes in path y
        for k in all_nodes:
            if k != intermediate_node and k != end_node:
                model.addConstr(gp.quicksum(y[i, k] for i in all_nodes
                                            if i != k) == gp.quicksum(
                                                y[k, j] for j in all_nodes
                                                if j != k),
                                name=f"FlowCons_y_{k}")
                # Ensure intermediate nodes are visited at most once
                model.addConstr(
                    gp.quicksum(y[i, k] for i in all_nodes if i != k) <= 1,
                    f"VisitOnce_y_{k}")

        # 11. Node Disjointness (except at C)
        # Nodes B, D (indices 1, 3) cannot be intermediate in both paths.
        # Node A (0) cannot be in path y. Node E (4) cannot be in path x.
        for k in all_nodes:
            if k != intermediate_node:  # For all nodes except C
                # If node k is entered in path x, it cannot be entered in path y
                model.addConstr(gp.quicksum(x[i, k]
                                            for i in all_nodes if i != k) +
                                gp.quicksum(y[i, k]
                                            for i in all_nodes if i != k) <= 1,
                                name=f"NodeDisjoint_{k}")

        # 12. Bandwidth Definition
        for i in all_nodes:
            for j in all_nodes:
                if i == j or bw_data[i][j] == 0:
                    continue  # Skip self-loops and zero-bandwidth links
                # If x[i,j] is 1, then B_overall <= bw_data[i][j]
                model.addConstr(B_overall <= bw_data[i][j] +
                                max_possible_bandwidth * (1 - x[i, j]),
                                name=f"B_limit_x_{i}_{j}")
                # If y[i,j] is 1, then B_overall <= bw_data[i][j]
                model.addConstr(B_overall <= bw_data[i][j] +
                                max_possible_bandwidth * (1 - y[i, j]),
                                name=f"B_limit_y_{i}_{j}")

        # Suppress Gurobi output to console if desired
        # model.setParam('OutputFlag', 0)
        model.setParam('MIPGap', 0.001)  # Set a small MIP gap

        # Optimize the model
        model.optimize()

        # --- Results ---
        if model.status == GRB.OPTIMAL:
            print("Optimal link arrangement found.")
            print(
                f"Maximum Path Bandwidth (A through C to E): {B_overall.X:.2f}"
            )

            path_AC_str = nodes_rev_map[start_node]
            curr = start_node
            visited_in_ac = {start_node}
            for _ in range(num_nodes):  # Max possible length
                found_next = False
                for j_node in all_nodes:
                    if curr != j_node and x[curr, j_node].X > 0.5:
                        path_AC_str += f" -> {nodes_rev_map[j_node]}"
                        curr = j_node
                        visited_in_ac.add(curr)
                        found_next = True
                        break
                if curr == intermediate_node or not found_next:
                    break
            print(f"  Path A to C: {path_AC_str}")

            path_CE_str = nodes_rev_map[intermediate_node]
            curr = intermediate_node
            visited_in_ce = {intermediate_node}
            for _ in range(num_nodes):  # Max possible length
                found_next = False
                for j_node in all_nodes:
                    if curr != j_node and y[curr, j_node].X > 0.5:
                        path_CE_str += f" -> {nodes_rev_map[j_node]}"
                        curr = j_node
                        visited_in_ce.add(curr)
                        found_next = True
                        break
                if curr == end_node or not found_next:
                    break
            print(f"  Path C to E: {path_CE_str}")

            print("\n  Links used in A-C path and their bandwidths:")
            for i in all_nodes:
                for j in all_nodes:
                    if i != j and x[i, j].X > 0.5:
                        print(
                            f"    {nodes_rev_map[i]} -> {nodes_rev_map[j]} (BW: {bw_data[i][j]})"
                        )

            print("  Links used in C-E path and their bandwidths:")
            for i in all_nodes:
                for j in all_nodes:
                    if i != j and y[i, j].X > 0.5:
                        print(
                            f"    {nodes_rev_map[i]} -> {nodes_rev_map[j]} (BW: {bw_data[i][j]})"
                        )

        elif model.status == GRB.INFEASIBLE:
            print(
                "Model is infeasible. No path from A to E via C could be found or satisfies constraints."
            )
            # Compute and print IIS (Irreducible Inconsistent Subsystem)
            model.computeIIS()
            model.write("bandwidth_path_iis.ilp")
            print("IIS written to bandwidth_path_iis.ilp for debugging.")
        else:
            print(f"Optimization stopped with status: {model.status}")
            if model.SolCount == 0:
                print("No feasible solution found.")

    except gp.GurobiError as e:
        print(f"Gurobi error code {e.errno}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == '__main__':
    solve_max_bandwidth_path()
