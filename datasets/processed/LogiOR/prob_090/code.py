import gurobipy as gp
from gurobipy import GRB
from typing import List, Dict

def solve_scooter_deployment(
    zones: List[str] = ['Commercial Center', 'University City', 'Tech Park', 'Tourist Area', 'Transit Hub'],
    attractiveness: Dict[str, int] = {
        'Commercial Center': 500,
        'University City': 800,
        'Tech Park': 700,
        'Tourist Area': 600,
        'Transit Hub': 900
    },
    total_scooters: int = 1000,
    min_quota_factor: float = 0.1,
    adjacency_limit: int = 50,
    cluster_capacity: int = 600
):
    """
    Solves the shared e-scooter network balancing problem using Gurobi.

    Args:
        zones (List[str]): A list of hotspot zone names.
        attractiveness (Dict[str, int]): A dictionary mapping each zone to its attractiveness value.
        total_scooters (int): The total number of scooters to be deployed.
        min_quota_factor (float): The factor of the total fleet size used for calculating the minimum deployment quota.
        adjacency_limit (int): The maximum allowed difference in deployment for adjacent key zones.
        cluster_capacity (int): The maximum number of scooters an operational cluster can manage.
    """
    # --- 1. Setup and Pre-calculation ---
    num_zones = len(zones)
    if num_zones == 0:
        return {"status": "error", "message": "The list of zones cannot be empty."}

    total_attractiveness = sum(attractiveness.values())

    # --- 2. Gurobi Model Initialization ---
    model = gp.Model("ScooterDeployment_Complex")

    # --- 3. Define Decision Variables ---
    # n[i]: number of scooters deployed in zone i
    n = model.addVars(zones, name="deployment", vtype=GRB.INTEGER, lb=0)

    # --- 4. Set Objective Function ---
    # Objective: Minimize the deviation from an ideal, attractiveness-weighted deployment.
    target_deployments = {}
    if total_attractiveness > 0:
        for i in zones:
            target_deployments[i] = total_scooters * (attractiveness[i] / total_attractiveness)
    else: # Handle case of zero total attractiveness
        avg_deployment = total_scooters / num_zones
        for i in zones:
            target_deployments[i] = avg_deployment

    # The objective is the sum of squared differences from this new weighted target.
    imbalance = gp.quicksum((n[i] - target_deployments[i]) * (n[i] - target_deployments[i]) for i in zones)
    model.setObjective(imbalance, GRB.MINIMIZE)

    # --- 5. Add Constraints ---
    # Constraint 1: Total Deployment Constraint
    model.addConstr(gp.quicksum(n[i] for i in zones) == total_scooters, "TotalDeployment")

    # Constraint 2: Minimum Quota Constraint
    if total_attractiveness > 0:
        for i in zones:
            min_quota = total_scooters * min_quota_factor * (attractiveness[i] / total_attractiveness)
            model.addConstr(n[i] >= min_quota, f"MinQuota_{i}")

    # Constraint 3: Adjacency Constraint
    # The absolute difference between 'Commercial Center' and 'Transit Hub' must not exceed the limit.
    model.addConstr(n['Commercial Center'] - n['Transit Hub'] <= adjacency_limit, "Adjacency_Upper")
    model.addConstr(n['Commercial Center'] - n['Transit Hub'] >= -adjacency_limit, "Adjacency_Lower")

    # Constraint 4: Operational Cluster Capacity Constraints
    # Cluster 1: Commercial Center, Tourist Area
    model.addConstr(n['Commercial Center'] + n['Tourist Area'] <= cluster_capacity, "Cluster1_Capacity")
    # Cluster 2: University City, Tech Park, Transit Hub
    model.addConstr(n['University City'] + n['Tech Park'] + n['Transit Hub'] <= cluster_capacity, "Cluster2_Capacity")
    
    # --- 6. Solve the Model ---
    model.optimize()

    # --- 7. Return Results ---
    if model.Status == GRB.OPTIMAL:
        return {"status": "optimal", "obj": model.ObjVal}
    else:
        return {"status": f"{model.Status}"}


if __name__ == "__main__":
    result = solve_scooter_deployment()
    print(result)
