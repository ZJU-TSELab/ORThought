import gurobipy as gp
from gurobipy import GRB


def solve_solvent_blending_optimization(
    Availability=[12000, 10500, 8000, 5000, 999999],
    Cost=[15, 12, 10, 18, 16],
    PropertyValue=[
        [95, 45, 150, 0.85],
        [88, 55, 180, 0.92],
        [82, 60, 200, 0.89],
        [105, 40, 130, 0.87],
        [100, 50, 160, 0.91]
    ],
    SolventPropertyValue=[
        [85, 50, 140, 0.88],
        [92, 50, 140, 0.88]
    ],
    Demand=[8500, 25000],
    SellingPrice=[25.50, 28.75],
    MaxBetaPercentage=0.35
):
    """
    Models and solves the solvent blending optimization problem.
    """
    # Create a new model
    model = gp.Model("Solvent Blending Optimization")

    # Sets
    Solvents = range(len(Demand))
    RawMaterials = range(len(Cost))
    Properties = range(len(PropertyValue[0]))

    # Decision Variables
    AmountProduced = {}
    for s in Solvents:
        for r in RawMaterials:
            AmountProduced[s, r] = model.addVar(
                vtype=GRB.CONTINUOUS,
                name=f"AmountProduced_{s+1}_{r+1}"
            )

    # Objective: Maximize profit (revenue from demand only - total production cost)
    total_revenue = gp.quicksum(SellingPrice[s] * Demand[s] for s in Solvents)
    total_cost = gp.quicksum(
        Cost[r] * gp.quicksum(AmountProduced[s, r] for s in Solvents)
        for r in RawMaterials
    )
    model.setObjective(total_revenue - total_cost, GRB.MAXIMIZE)

    # Constraint 1: Demand constraint (production must meet exactly the demand)
    for s in Solvents:
        model.addConstr(
            gp.quicksum(AmountProduced[s, r] for r in RawMaterials) == Demand[s],
            f"Demand_{s+1}"
        )

    # Constraint 2: Availability constraint
    for r in RawMaterials:
        model.addConstr(
            gp.quicksum(AmountProduced[s, r] for s in Solvents) <= Availability[r],
            f"Availability_{r+1}"
        )

    # Constraint 3: Property constraints
    for s in Solvents:
        # For properties 0 (VI) and 2 (Boiling Point) - minimum requirements
        for p in [0, 2]:
            model.addConstr(
                gp.quicksum(PropertyValue[r][p] * AmountProduced[s, r] for r in RawMaterials) >=
                SolventPropertyValue[s][p] * gp.quicksum(AmountProduced[s, r] for r in RawMaterials),
                f"MinProperty_{s+1}_{p+1}"
            )

        # For properties 1 (Flash Point) and 3 (Density) - exact requirements
        for p in [1, 3]:
            model.addConstr(
                gp.quicksum(PropertyValue[r][p] * AmountProduced[s, r] for r in RawMaterials) ==
                SolventPropertyValue[s][p] * gp.quicksum(AmountProduced[s, r] for r in RawMaterials),
                f"ExactProperty_{s+1}_{p+1}"
            )

    # Constraint 4: Beta constraint (raw material 1 is Beta)
    for s in Solvents:
        model.addConstr(
            AmountProduced[s, 1] <= MaxBetaPercentage * gp.quicksum(AmountProduced[s, r] for r in RawMaterials),
            f"BetaLimit_{s+1}"
        )

    # Optimize the model
    model.optimize()

    # Return Results
    if model.status == GRB.OPTIMAL:
        return {"status": "optimal", "obj": model.ObjVal}
    else:
        return {"status": f"{model.status}"}


if __name__ == "__main__":
    result = solve_solvent_blending_optimization()
    print(result)
