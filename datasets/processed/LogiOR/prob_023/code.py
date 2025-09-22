import gurobipy as gp
from gurobipy import GRB


def solve_chemical_mixing(
    chemical_cost=[8, 10, 11, 14],
    ingredient_content=[
        [0.03, 0.02, 0.01],  # Chemical 1
        [0.06, 0.04, 0.01],  # Chemical 2
        [0.10, 0.03, 0.04],  # Chemical 3
        [0.12, 0.09, 0.04]  # Chemical 4
    ],
    ingredient_min=[0.08, 0.04, 0.02],
    chemical_min=[0, 100, 0, 0],
    produce_target=1000):
    """
    Solves the chemical mixing problem to minimize cost.
    """
    # --- 1. Model Creation ---
    model = gp.Model("ChemicalMixing")

    # --- 2. Parameters & Sets ---
    chemicals = range(len(chemical_cost))
    ingredients = range(len(ingredient_min))

    # --- 3. Decision Variables ---
    chemical_amount = model.addVars(chemicals, lb=0, name="ChemicalAmount")

    # --- 4. Objective Function ---
    # Minimize the total cost
    model.setObjective(chemical_amount.prod(chemical_cost), GRB.MINIMIZE)

    # --- 5. Constraints ---
    # Constraint 1: Ingredient minimum content
    model.addConstrs(
        (gp.quicksum(ingredient_content[i][j] * chemical_amount[i]
                     for i in chemicals) >= ingredient_min[j] * produce_target
         for j in ingredients), "IngredientMin")

    # Constraint 2: Chemical minimum content
    model.addConstrs((chemical_amount[i] >= chemical_min[i] for i in chemicals),
                     "ChemicalMin")

    # Constraint 3: Total amount constraint
    model.addConstr(
        chemical_amount.sum() == produce_target,
        "TotalAmount")

    # --- 6. Solve the Model ---
    model.optimize()

    # --- 7. Return Results ---
    if model.status == GRB.OPTIMAL:
        return {"status": "optimal", "obj": model.ObjVal}
    else:
        return {"status": f"{model.status}"}


# Run the solver function
if __name__ == "__main__":
    result = solve_chemical_mixing()
    print(result)