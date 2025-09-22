import gurobipy as gp
from gurobipy import GRB
from typing import List, Dict, Tuple
import math

def solve_food_bank_routing(
    supermarkets: Dict[str, Tuple[int, int]] = {
        'S1': (5, 10),
        'S2': (12, 8),
        'S3': (-10, 5),
        'S4': (0, -15),
        'S5': (-15, -10),
        'S6': (15, -5),
        'S7': (8, 18),
        'S8': (-5, -20)
    },
    items: Dict[str, Dict] = {
        # S1 Items
        'Milk':       {'supermarket': 'S1', 'volume': 0.8, 'weight': 150, 'priority': 80},
        'Cheese':     {'supermarket': 'S1', 'volume': 0.3, 'weight': 50,  'priority': 65},
        # S2 Items
        'Bread':      {'supermarket': 'S2', 'volume': 1.0, 'weight': 100, 'priority': 50},
        'Vegetables': {'supermarket': 'S2', 'volume': 0.5, 'weight': 80,  'priority': 40},
        # S3 Items
        'Frozen Meat':{'supermarket': 'S3', 'volume': 0.6, 'weight': 200, 'priority': 100},
        'Pasta':      {'supermarket': 'S3', 'volume': 0.4, 'weight': 60,  'priority': 45},
        # S4 Items
        'Fruit':      {'supermarket': 'S4', 'volume': 0.7, 'weight': 120, 'priority': 60},
        'Yogurt':     {'supermarket': 'S4', 'volume': 0.4, 'weight': 100, 'priority': 70},
        'Berries':    {'supermarket': 'S4', 'volume': 0.2, 'weight': 30,  'priority': 55},
        # S5 Items
        'Eggs':       {'supermarket': 'S5', 'volume': 0.3, 'weight': 40,  'priority': 75},
        'Butter':     {'supermarket': 'S5', 'volume': 0.2, 'weight': 50,  'priority': 50},
        # S6 Items
        'Sausages':   {'supermarket': 'S6', 'volume': 0.5, 'weight': 110, 'priority': 90},
        'Fish Fillets':{'supermarket': 'S6', 'volume': 0.4, 'weight': 90, 'priority': 95},
        # S7 Items
        'Juice':      {'supermarket': 'S7', 'volume': 0.6, 'weight': 120, 'priority': 30},
        'Canned Soup':{'supermarket': 'S7', 'volume': 0.8, 'weight': 150, 'priority': 25},
        # S8 Items
        'Salad Mix':  {'supermarket': 'S8', 'volume': 0.9, 'weight': 70,  'priority': 35},
    },
    depot_coords: Tuple[int, int] = (0, 0),
    truck_volume_capacity: float = 2.0,
    truck_weight_capacity: float = 500.0,
    max_time_mins: int = 240,
    truck_speed_kmh: int = 40,
    loading_time_mins: int = 20,
    M: int = 10000 # A large number for MTZ constraints
):
    """
    Solves the Food Bank Vehicle Routing Problem with Profits using Gurobi.

    Args:
        supermarkets (Dict[str, Tuple[int, int]]): A dictionary mapping supermarket IDs to their (x, y) coordinates.
        items (Dict[str, Dict]): A dictionary mapping item names to their properties.
        depot_coords (Tuple[int, int]): The (x, y) coordinates of the food bank depot.
        truck_volume_capacity (float): The maximum volume capacity of the truck (m³).
        truck_weight_capacity (float): The maximum weight capacity of the truck (kg).
        max_time_mins (int): The total available time for the route in minutes.
        truck_speed_kmh (int): The constant speed of the truck in km/h.
        loading_time_mins (int): The fixed time spent loading at each visited supermarket.
        M (int): A sufficiently large number for Big-M method constraints.
    """

    # --- 1. Data Pre-processing ---
    depot_id = 'Depot'
    supermarket_ids = list(supermarkets.keys())
    nodes = [depot_id] + supermarket_ids
    node_coords = {depot_id: depot_coords, **supermarkets}
    num_nodes = len(nodes)
    item_ids = list(items.keys())

    # Pre-calculate travel times between all nodes
    def euclidean_distance(p1, p2):
        return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

    travel_times = {}
    for j in nodes:
        for k in nodes:
            if j == k:
                continue
            dist = euclidean_distance(node_coords[j], node_coords[k])
            time_mins = (dist / truck_speed_kmh) * 60
            travel_times[j, k] = time_mins

    # --- 2. Gurobi Model Initialization ---
    model = gp.Model("FoodBankRouting")

    # --- 3. Define Decision Variables ---
    # c[i]: 1 if item i is collected, 0 otherwise
    c = model.addVars(item_ids, name="Collect", vtype=GRB.BINARY)
    # y[j]: 1 if supermarket j is visited, 0 otherwise
    y = model.addVars(supermarket_ids, name="Visit", vtype=GRB.BINARY)
    # z[j,k]: 1 if truck travels from node j to node k, 0 otherwise
    z = model.addVars(nodes, nodes, name="Arc", vtype=GRB.BINARY)
    # u[j]: Auxiliary variable for MTZ subtour elimination
    u = model.addVars(nodes, name="MTZ_u", vtype=GRB.CONTINUOUS)

    # --- 4. Set Objective Function ---
    total_priority = gp.quicksum(items[i]['priority'] * c[i] for i in item_ids)
    model.setObjective(total_priority, GRB.MAXIMIZE)

    # --- 5. Add Constraints ---
    # Constraint 1: Volume Capacity
    model.addConstr(gp.quicksum(items[i]['volume'] * c[i] for i in item_ids) <= truck_volume_capacity, "VolumeCapacity")

    # Constraint 2: Weight Capacity
    model.addConstr(gp.quicksum(items[i]['weight'] * c[i] for i in item_ids) <= truck_weight_capacity, "WeightCapacity")

    # Constraint 3: Time Constraint
    total_travel_time = gp.quicksum(travel_times[j, k] * z[j, k] for j in nodes for k in nodes if j != k)
    total_loading_time = gp.quicksum(loading_time_mins * y[j] for j in supermarket_ids)
    model.addConstr(total_travel_time + total_loading_time <= max_time_mins, "TimeLimit")

    # Constraint 4: Item Collection Logic
    for i in item_ids:
        supermarket_of_item = items[i]['supermarket']
        model.addConstr(c[i] <= y[supermarket_of_item], f"CollectLogic_{i}")

    # Constraint 5: Routing Flow Conservation
    for j in supermarket_ids:
        # If a supermarket is visited, truck must enter and leave it exactly once
        model.addConstr(gp.quicksum(z[k, j] for k in nodes if k != j) == y[j], f"Flow_In_{j}")
        model.addConstr(gp.quicksum(z[j, k] for k in nodes if k != j) == y[j], f"Flow_Out_{j}")

    # Constraint 6: Depot Departure and Return
    model.addConstr(gp.quicksum(z[depot_id, k] for k in supermarket_ids) == 1, "Depot_Leave")
    model.addConstr(gp.quicksum(z[j, depot_id] for j in supermarket_ids) == 1, "Depot_Return")
    
    # Disallow travel from a node to itself
    for j in nodes:
        model.addConstr(z[j,j] == 0, f"No_Self_Loop_{j}")

    # Constraint 7: Subtour Elimination (MTZ formulation)
    for j in supermarket_ids:
        model.addConstr(u[j] >= 2, f"MTZ_Lower_{j}")
        model.addConstr(u[j] <= num_nodes, f"MTZ_Upper_{j}")

    for j in supermarket_ids:
        for k in supermarket_ids:
            if j != k:
                model.addConstr(u[j] - u[k] + num_nodes * z[j, k] <= num_nodes - 1, f"MTZ_Main_{j}_{k}")

    # --- 6. Solve the Model ---
    model.optimize()

    # --- 7. Return Results ---
    if model.Status == GRB.OPTIMAL:
        return {"status": "optimal", "obj": model.ObjVal}
    else:
        return {"status": f"{model.Status}"}


if __name__ == "__main__":
    result = solve_food_bank_routing()
    print(result)
