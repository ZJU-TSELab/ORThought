import gurobipy as gp
from gurobipy import GRB


def solve_supplier_shipment_optimization(
    CostPerShipment=[5.2, 4.7, 3.5],
    Percent=[
        [45, 35, 20],
        [30, 45, 25],
        [15, 20, 65]
    ],
    Demand=[500, 300, 300],
    MaxShipment=[700, 700, 700]
):
    # Create a new model
    model = gp.Model("Supplier Shipment Optimization")

    # Sets
    Suppliers = range(len(CostPerShipment))
    ShipmentTypes = range(len(Demand))

    # Decision Variables
    ShipmentNum = model.addVars(Suppliers, vtype=GRB.INTEGER, name="ShipmentNum")

    # Objective: Minimize total cost of shipments
    obj = gp.quicksum(CostPerShipment[s] * ShipmentNum[s] for s in Suppliers)
    model.setObjective(obj, GRB.MINIMIZE)

    # Constraint 1: Shipment number constraint (cannot exceed maximum)
    for s in Suppliers:
        model.addConstr(
            ShipmentNum[s] <= MaxShipment[s],
            f"MaxShipment_{s+1}"
        )

    # Constraint 2: Demand satisfaction constraint
    for t in ShipmentTypes:
        # Convert percentage to decimal
        model.addConstr(
            gp.quicksum((Percent[s][t] / 100) * ShipmentNum[s] for s in Suppliers) >= Demand[t],
            f"DemandSatisfaction_{t+1}"
        )

    # Optimize the model
    model.optimize()

    # Return results
    if model.status == GRB.OPTIMAL:
        return {"status": "optimal", "obj": model.objVal}
    else:
        return {"status": f"{model.status}"}


if __name__ == "__main__":
    result = solve_supplier_shipment_optimization()
    print(result)