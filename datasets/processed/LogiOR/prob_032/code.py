import gurobipy as gp
from gurobipy import GRB

def solve_waste_treatment_optimization(
    TreatmentCost=[12, 8, 18],
    PollutantReduction=[
        [0.15, 0.35],
        [0.25, 0.20],
        [0.30, 0.40]
    ],
    PollutionTarget=[25, 35]
):
    # Create a new model
    model = gp.Model("Waste Treatment Optimization")

    # Sets
    Facilities = range(len(TreatmentCost))
    Pollutants = range(len(PollutionTarget))

    # Decision Variables
    TreatmentAmount = model.addVars(Facilities, vtype=GRB.CONTINUOUS, name="TreatmentAmount")

    # Objective: Minimize total treatment cost
    obj = gp.quicksum(TreatmentCost[f] * TreatmentAmount[f] for f in Facilities)
    model.setObjective(obj, GRB.MINIMIZE)

    # Constraint 1: Pollution reduction constraint
    for p in Pollutants:
        model.addConstr(
            gp.quicksum(PollutantReduction[f][p] * TreatmentAmount[f] for f in Facilities) >= PollutionTarget[p],
            f"PollutionReduction_{p+1}"
        )

    # Optimize the model
    model.optimize()

    # Return Results
    if model.status == GRB.OPTIMAL:
        return {"status": "optimal", "obj": model.ObjVal}
    else:
        return {"status": f"{model.status}"}


if __name__ == "__main__":
    result = solve_waste_treatment_optimization()
    print(result)