import gurobipy as gp
from gurobipy import GRB

def solve_blood_center_location(
    candidate_cities=[1, 2, 3, 4],
    hospitals=[1, 2, 3],
    construction_cost={1: 8, 2: 7, 3: 9, 4: 7.5},
    distances_matrix=[[50, 80, 120], [60, 40, 90], [110, 70, 50], [130, 100, 60]],
    num_to_select=2,
    max_joint_failure_prob=0.1,
    prob_coeff=0.00005
):
    """
    Solve the blood center location problem using Gurobi.
    The model aims to minimize construction cost while satisfying the number of centers and supply reliability constraints.
    """
    # Create a new model
    model = gp.Model("BloodCenterLocation")

    # Convert distance data to a dictionary for easy access
    distances = {(c, h): distances_matrix[c-1][h-1]
                 for c in candidate_cities for h in hospitals}

    # --- Decision Variables ---
    # 1 if a center is built in city c, 0 otherwise
    select_city = model.addVars(candidate_cities, vtype=GRB.BINARY, name="SelectCity")
    
    # Auxiliary variable for joint failure probability for each hospital
    joint_failure_prob = model.addVars(hospitals, vtype=GRB.CONTINUOUS, 
                                       lb=0, ub=1, name="JointFailureProb")

    # --- Objective Function: Minimize Total Construction Cost ---
    total_construction_cost = gp.quicksum(construction_cost[c] * select_city[c]
                                          for c in candidate_cities)
    model.setObjective(total_construction_cost, GRB.MINIMIZE)

    # --- Constraints ---

    # 1. The total number of centers built must equal the specified number
    model.addConstr(select_city.sum('*') == num_to_select, name="TotalCentersConstraint")

    # 2. Supply reliability constraint for each hospital (nonlinear constraint)
    for h in hospitals:
        # Expression for joint failure probability
        joint_failure_prob_expr = 1
        for c in candidate_cities:
            fail_prob_ch = prob_coeff * (distances[c, h] ** 2)
            term = (1 - select_city[c]) + select_city[c] * fail_prob_ch
            joint_failure_prob_expr *= term
        
        # Use equality constraint to define auxiliary variable
        model.addConstr(joint_failure_prob[h] == joint_failure_prob_expr,
                        name=f"JointFailureProb_Hospital_{h}")
        
        # Add linear constraint for reliability requirement
        model.addConstr(joint_failure_prob[h] <= max_joint_failure_prob,
                        name=f"Reliability_Hospital_{h}")

    # --- Solve ---
    # Gurobi needs to know the model is non-convex
    model.params.NonConvex = 2
    model.optimize()

    # --- Return Results ---
    if model.status == GRB.OPTIMAL:
        return {"status": "optimal", "obj": model.objVal}
    else:
        return {"status": f"{model.status}"}


# Run the solver function
if __name__ == '__main__':
    result = solve_blood_center_location()
    print(result)