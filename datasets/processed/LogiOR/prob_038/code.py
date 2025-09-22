import gurobipy as gp
from gurobipy import GRB


def solve_component_manufacturing_optimization(
    RawMaterialCost=60,
    ComponentPerRawMaterial=[7, 3, 0],
    EnergyCostPerRawMaterial=8,
    MachineTimePerRawMaterial=7,
    SellingPrice=[25, 35, 45],
    Engine2TransmissionCost=5,
    Engine2TransmissionMachineTime=4,
    Engine2BrakeSystemCost=10,
    Engine2BrakeSystemMachineTime=6,
    Transmission2BrakeSystemCost=12,
    Transmission2BrakeSystemMachineTime=5,
    MaxMachineTime=60000,
    MinBrakeSystemProduction=4000,
    MaxDemand=[20000, 15000, 12000]
):
    """
    Models and solves the component manufacturing and processing optimization problem.
    """
    # Create a new model
    model = gp.Model("Component Manufacturing and Processing Optimization")

    # Sets
    Components = range(len(SellingPrice))

    # Decision Variables
    RawMaterialPurchased = model.addVar(vtype=GRB.INTEGER, name="RawMaterialPurchased")
    ComponentProducedfromRawMaterial = model.addVars(Components, vtype=GRB.INTEGER, name="ComponentProducedfromRawMaterial")
    Engine2TransmissionProduced = model.addVar(vtype=GRB.INTEGER, name="Engine2TransmissionProduced")
    Engine2BrakeSystemProduced = model.addVar(vtype=GRB.INTEGER, name="Engine2BrakeSystemProduced")
    Transmission2BrakeSystemProduced = model.addVar(vtype=GRB.INTEGER, name="Transmission2BrakeSystemProduced")
    ComponentSold = model.addVars(Components, vtype=GRB.INTEGER, name="ComponentSold")

    # Objective: Maximize total profit
    revenue = gp.quicksum(SellingPrice[c] * ComponentSold[c] for c in Components)
    raw_material_cost = (RawMaterialCost + EnergyCostPerRawMaterial) * RawMaterialPurchased
    processing_cost = (Engine2TransmissionCost * Engine2TransmissionProduced +
                       Engine2BrakeSystemCost * Engine2BrakeSystemProduced +
                       Transmission2BrakeSystemCost * Transmission2BrakeSystemProduced)

    model.setObjective(revenue - raw_material_cost - processing_cost, GRB.MAXIMIZE)

    # Constraint 1: Machine time constraint
    machine_time = (MachineTimePerRawMaterial * RawMaterialPurchased +
                    Engine2TransmissionMachineTime * Engine2TransmissionProduced +
                    Engine2BrakeSystemMachineTime * Engine2BrakeSystemProduced +
                    Transmission2BrakeSystemMachineTime * Transmission2BrakeSystemProduced)
    model.addConstr(machine_time <= MaxMachineTime, "MachineTime")

    # Constraint 2: Minimum Brake System production constraint
    model.addConstr(
        Engine2BrakeSystemProduced + Transmission2BrakeSystemProduced >= MinBrakeSystemProduction,
        "MinBrakeSystemProduction"
    )

    # Constraint 3: Demand constraint
    for c in Components:
        model.addConstr(ComponentSold[c] <= MaxDemand[c], f"MaxDemand_{c}")

    # Constraint 4: Production constraint - components from raw material
    for c in Components:
        model.addConstr(
            ComponentProducedfromRawMaterial[c] == ComponentPerRawMaterial[c] * RawMaterialPurchased,
            f"RawMaterialProduction_{c}"
        )

    # Constraint 5: Production constraint - Engine Block
    model.addConstr(
        ComponentSold[0] == ComponentProducedfromRawMaterial[0] - Engine2TransmissionProduced - Engine2BrakeSystemProduced,
        "EngineBlockBalance"
    )

    # Constraint 6: Production constraint - Transmission
    model.addConstr(
        ComponentSold[1] == ComponentProducedfromRawMaterial[1] + Engine2TransmissionProduced - Transmission2BrakeSystemProduced,
        "TransmissionBalance"
    )

    # Constraint 7: Production constraint - Brake System
    model.addConstr(
        ComponentSold[2] == ComponentProducedfromRawMaterial[2] + Engine2BrakeSystemProduced + Transmission2BrakeSystemProduced,
        "BrakeSystemBalance"
    )

    # Optimize the model
    model.optimize()

    # Return Results
    if model.status == GRB.OPTIMAL:
        return {"status": "optimal", "obj": model.ObjVal}
    else:
        return {"status": f"{model.status}"}


if __name__ == "__main__":
    result = solve_component_manufacturing_optimization()
    print(result)
