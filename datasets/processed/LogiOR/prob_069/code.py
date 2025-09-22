import gurobipy as gp
from gurobipy import GRB

def solve_max_flow(
    nodes=['A', 'B', 'C', 'D', 'E', 'F', 'G'],
    arcs={
        ('A', 'B'): 15,
        ('A', 'C'): 10,
        ('B', 'C'): 5,
        ('B', 'D'): 10,
        ('C', 'E'): 8,
        ('C', 'F'): 12,
        ('E', 'D'): 7,
        ('F', 'D'): 20,
        ('G', 'D'): 0
    }
):
    """Solve the maximum flow problem for water distribution network."""
    
    model = gp.Model("WaterDistributionMaxFlow")
    
    active_arcs = {k: v for k, v in arcs.items() if v > 0}
    
    flow = model.addVars(active_arcs.keys(), name="flow")
    
    model.setObjective(flow.sum('A', '*'), GRB.MAXIMIZE)
    
    model.addConstrs((flow[i,j] <= active_arcs[i,j] for i,j in active_arcs), "capacity")
    
    intermediate_nodes = [n for n in nodes if n not in ['A', 'D']]
    
    for node in intermediate_nodes:
        inflow = gp.quicksum(flow[i,j] for i,j in active_arcs if j == node)
        outflow = gp.quicksum(flow[i,j] for i,j in active_arcs if i == node)
        model.addConstr(inflow == outflow, f"flow_conserv_{node}")
    
    model.optimize()
    
    if model.status == GRB.OPTIMAL:
        return {"status": "optimal", "obj": model.objVal}
    else:
        return {"status": f"{model.status}"}

if __name__ == "__main__":
    result = solve_max_flow()
    print(result)