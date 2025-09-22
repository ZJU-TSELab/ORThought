import gurobipy as gp
from gurobipy import GRB

def solve_cross_docking_qap(
    inbound_shipments=['S1', 'S2', 'S3', 'S4'],
    outbound_shipments=['R1', 'R2', 'R3'],
    inbound_docks=['I1', 'I2', 'I3', 'I4'],
    outbound_docks=['O1', 'O2', 'O3'],
    zones=['A', 'B'],
    shipment_items={
        'S1': 200, 'S2': 150, 'S3': 180, 'S4': 220,
        'R1': 250, 'R2': 300, 'R3': 200
    },
    dock_zones={
        'I1': 'A', 'I2': 'A', 'O1': 'A',
        'I3': 'B', 'I4': 'B', 'O2': 'B', 'O3': 'B'
    },
    congestion_coeffs={'A': 0.00005, 'B': 0.00004},
    base_handling_cost_per_item=0.1
):
    """
    Solves the Cross-Docking Center dock assignment problem to minimize
    the total internal handling cost. This is a Quadratic Assignment Problem (QAP)
    due to the non-linear congestion cost function.
    """
    # Create a new model
    model = gp.Model("CrossDockingCenter")

    # --- Decision Variables ---
    # Binary variable: 1 if an inbound shipment is assigned to an inbound dock
    assign_inbound = model.addVars(inbound_shipments, inbound_docks, vtype=GRB.BINARY, name="AssignInbound")
    
    # Binary variable: 1 if an outbound shipment is assigned to an outbound dock
    assign_outbound = model.addVars(outbound_shipments, outbound_docks, vtype=GRB.BINARY, name="AssignOutbound")

    # --- Constraints (Assignment Logic) ---
    # 1. Each inbound shipment must be assigned to exactly one inbound dock.
    model.addConstrs((assign_inbound.sum(s, '*') == 1 for s in inbound_shipments), name="AssignEachInboundShipment")
    
    # 2. Each inbound dock can only be assigned to one inbound shipment.
    model.addConstrs((assign_inbound.sum('*', i) == 1 for i in inbound_docks), name="AssignEachInboundDock")

    # 3. Each outbound shipment must be assigned to exactly one outbound dock.
    model.addConstrs((assign_outbound.sum(r, '*') == 1 for r in outbound_shipments), name="AssignEachOutboundShipment")

    # 4. Each outbound dock can only be assigned to one outbound shipment.
    model.addConstrs((assign_outbound.sum('*', o) == 1 for o in outbound_docks), name="AssignEachOutboundDock")
    
    # --- Objective Function: Minimize Total Cost ---
    
    # 1. Calculate total items flowing through each zone based on assignments
    items_in_zone = {}
    for z in zones:
        inbound_items_in_zone = gp.quicksum(
            assign_inbound[s, i] * shipment_items[s] 
            for s, i in assign_inbound if dock_zones[i] == z
        )
        outbound_items_in_zone = gp.quicksum(
            assign_outbound[r, o] * shipment_items[r] 
            for r, o in assign_outbound if dock_zones[o] == z
        )
        items_in_zone[z] = inbound_items_in_zone + outbound_items_in_zone

    # 2. Calculate the non-linear congestion cost
    congestion_cost = gp.quicksum(
        congestion_coeffs[z] * items_in_zone[z] * items_in_zone[z] for z in zones
    )
    
    # 3. Calculate the fixed base handling cost
    total_items = sum(shipment_items.values())
    base_cost = base_handling_cost_per_item * total_items
    
    model.setObjective(congestion_cost + base_cost, GRB.MINIMIZE)

    # Optimize the model
    model.optimize()

    # --- Return Results ---
    if model.status == GRB.OPTIMAL:
        return {"status": "optimal", "obj": model.objVal}
    else:
        return {"status": f"{model.status}"}


# Run the solver function
if __name__ == '__main__':
    result = solve_cross_docking_qap()
    print(result)