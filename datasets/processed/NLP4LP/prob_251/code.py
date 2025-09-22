def optimize_transportation(min_people=550, max_motor_trips=25, kayak_time=5, motor_time=3, min_kayak_ratio=0.75):
    from gurobipy import Model, GRB
    
    # Create a new model
    m = Model("LakeTransport")
    
    # Decision variables
    # k: number of kayak trips
    # m_trips: number of motorboat trips
    k = m.addVar(vtype=GRB.INTEGER, name="kayak_trips", lb=0)
    m_trips = m.addVar(vtype=GRB.INTEGER, name="motorboat_trips", lb=0)
    
    # Set objective: minimize total time
    m.setObjective(kayak_time * k + motor_time * m_trips, GRB.MINIMIZE)
    
    # Add constraints
    # Capacity constraint: at least min_people transported
    m.addConstr(4 * k + 5 * m_trips >= min_people, "capacity")
    
    # Motorboat trip limit
    m.addConstr(m_trips <= max_motor_trips, "max_motor_trips")
    
    # Trip ratio constraint: at least 75% trips are by kayak
    m.addConstr(k >= 3 * m_trips, "trip_ratio")
    
    # Optimize the model
    m.optimize()
    
    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        total_time = m.objVal
        return total_time
    else:
        return None
# Example usage
if __name__ == "__main__":
    min_time = optimize_transportation()
    if min_time is not None:
        print(f"Minimum Total Time: {min_time}")
    else:
        print("No feasible solution found.")