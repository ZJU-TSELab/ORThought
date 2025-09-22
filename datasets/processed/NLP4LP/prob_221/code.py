def optimize_science_fair(
    min_participants=500,
    min_posters=300,
    max_space=1900
):
    import gurobipy as gp
    from gurobipy import GRB

    # Create a new model
    model = gp.Model("Science_Fair_Tables")

    # Decision variables: number of circular and rectangular tables
    x_c = model.addVar(vtype=GRB.INTEGER, name="Circular_Tables", lb=0)
    x_r = model.addVar(vtype=GRB.INTEGER, name="Rectangular_Tables", lb=0)

    # Set the objective: maximize total guests served
    model.setObjective(8 * x_c + 12 * x_r, GRB.MAXIMIZE)

    # Add constraints
    # Participants constraint
    model.addConstr(5 * x_c + 4 * x_r >= min_participants, "Participants")
    # Poster boards constraint
    model.addConstr(4 * x_c + 4 * x_r >= min_posters, "PosterBoards")
    # Space constraint
    model.addConstr(15 * x_c + 20 * x_r <= max_space, "Space")

    # Optimize the model
    model.optimize()

    # Check if a feasible solution was found
    if model.status == GRB.OPTIMAL:
        return model.objVal
    else:
        return None
# Example usage
if __name__ == "__main__":
    max_guests = optimize_science_fair()
    if max_guests is not None:
        print(f"Maximum Guests Served: {max_guests}")
    else:
        print("No feasible solution found.")