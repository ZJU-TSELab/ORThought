def optimize_annotation_distribution(
    total_images=10000,
    specialized_rate=60,
    common_rate=40,
    specialized_cost=100,
    common_cost=72
):
    import gurobipy as gp
    from gurobipy import GRB

    # Create a new model
    model = gp.Model("AnnotationCostMinimization")

    # Decision variables: number of images assigned to each company
    x = model.addVar(name="specialized_images", lb=0)
    y = model.addVar(name="common_images", lb=0)

    # Set the objective: minimize total cost
    # Cost per image for specialized company
    cost_per_image_specialized = specialized_cost / specialized_rate
    # Cost per image for common company
    cost_per_image_common = common_cost / common_rate

    model.setObjective(
        cost_per_image_specialized * x + cost_per_image_common * y,
        GRB.MINIMIZE
    )

    # Add constraints
    # Total images constraint
    model.addConstr(x + y >= total_images, name="total_images")
    # Minimum work for specialized company (at least one-third)
    model.addConstr(2 * x >= y, name="specialized_min_work")

    # Optimize the model
    model.optimize()

    # Check if a feasible solution was found
    if model.status == GRB.OPTIMAL:
        # Return the optimal total cost
        return model.objVal
    else:
        # No feasible solution
        return None
# Example usage
if __name__ == "__main__":
    min_cost = optimize_annotation_distribution()
    if min_cost is not None:
        print(f"Minimum Total Annotation Cost: {min_cost}")
    else:
        print("No feasible solution found.")