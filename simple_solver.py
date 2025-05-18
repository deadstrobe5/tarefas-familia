#!/usr/bin/env python3
import pulp
import sys
import json
import random
from collections import defaultdict
from itertools import combinations

# CONFIGURATION
PEOPLE = ["A", "C", "M", "P", "D", "H"]
PAIRS = list(combinations(PEOPLE, 2))

def solve_rotation_schedule(task_codes, weeks, time_limit=30, max_allowed_diff=None):
    """Solve for a fair rotation with two key constraints:
    1. Perfect pair rotation: everyone works with everyone else fairly
    2. Perfect task rotation: everyone does each task fairly"""
    print(f"Solving for {len(task_codes)} tasks over {weeks} weeks...")
    
    # Setup variables: x[person][task][week] = 1 if person is assigned to task in week
    x = pulp.LpVariable.dicts('x', (PEOPLE, task_codes, range(weeks)), 0, 1, pulp.LpBinary)
    y = pulp.LpVariable.dicts('y', (PEOPLE, PEOPLE, range(weeks)), 0, 1, pulp.LpBinary)
    prob = pulp.LpProblem('TaskRotation', pulp.LpMinimize)
    prob += 0  # Dummy objective

    # Each person does at most one task per week
    for p in PEOPLE:
        for w in range(weeks):
            prob += pulp.lpSum(x[p][t][w] for t in task_codes) <= 1

    # Each task gets exactly 2 people per week
    for t in task_codes:
        for w in range(weeks):
            prob += pulp.lpSum(x[p][t][w] for p in PEOPLE) == 2

    # Link y[p1][p2][w] = 1 if p1 and p2 work together in week w
    for w in range(weeks):
        for t in task_codes:
            for p1 in PEOPLE:
                for p2 in PEOPLE:
                    if p1 >= p2:
                        continue
                    # If both p1 and p2 are assigned to task t in week w, y[p1][p2][w] = 1
                    prob += y[p1][p2][w] >= x[p1][t][w] + x[p2][t][w] - 1
        
        # y can only be 1 if both people are assigned to a task
        for p1 in PEOPLE:
            for p2 in PEOPLE:
                if p1 >= p2:
                    continue
                prob += y[p1][p2][w] <= pulp.lpSum(x[p1][t][w] for t in task_codes)
                prob += y[p1][p2][w] <= pulp.lpSum(x[p2][t][w] for t in task_codes)

    # Perfect task rotation: in every block of len(task_codes) weeks, each person does each task exactly once
    task_block = len(task_codes)
    for p in PEOPLE:
        for block_start in range(0, weeks, task_block):
            block_weeks = [w for w in range(block_start, min(block_start + task_block, weeks))]
            for t in task_codes:
                prob += pulp.lpSum(x[p][t][w] for w in block_weeks) == 1

    # Try to ensure fair distribution of partners: everyone works with everyone fairly
    block_size = len(PEOPLE) - 1
    for p1 in PEOPLE:
        for block_start in range(0, weeks, block_size):
            block_weeks = [w for w in range(block_start, min(block_start + block_size, weeks))]
            for p2 in PEOPLE:
                if p1 == p2:
                    continue
                prob += pulp.lpSum(y[min(p1,p2)][max(p1,p2)][w] for w in block_weeks) >= 1
                prob += pulp.lpSum(y[min(p1,p2)][max(p1,p2)][w] for w in block_weeks) <= 2

    # Solve the model
    print(f"Solving with {time_limit} second time limit...")
    solver = pulp.PULP_CBC_CMD(msg=False, timeLimit=time_limit)
    prob.solve(solver)
    status = pulp.LpStatus[prob.status]
    print(f"Solution status: {status}")
    
    if status != 'Optimal':
        return None
        
    # Extract the solution
    schedule = []
    for w in range(weeks):
        week_assignments = {}
        for t in task_codes:
            assigned = [p for p in PEOPLE if pulp.value(x[p][t][w]) > 0.5]
            if len(assigned) == 2:
                week_assignments[t] = tuple(assigned)
        schedule.append(week_assignments)
    
    # Check fairness of pairing distribution
    min_pair, max_pair, _ = get_pairing_stats(schedule)
    diff = max_pair - min_pair
    print(f"Pairing distribution - min: {min_pair}, max: {max_pair}, diff: {diff}")
    
    if max_allowed_diff is not None and diff > max_allowed_diff:
        print(f"[ERROR] Output solution violates max-min diff constraint!")
        return None
        
    return schedule

def get_pairing_stats(schedule):
    """Calculate statistics about partner pairings"""
    pair_counts = defaultdict(int)
    for week in schedule:
        for task, pair in week.items():
            p1, p2 = sorted(pair)
            pair_counts[(p1, p2)] += 1
    counts = list(pair_counts.values())
    return min(counts), max(counts), pair_counts

def solve_with_randomness(task_codes, weeks=18, num_iterations=5, time_limit=30):
    """Try multiple solutions with randomness and pick the best one"""
    print(f"Generating {num_iterations} random solutions for {weeks} weeks...")
    
    best_schedule = None
    best_diff = None
    best_stats = None
    
    for i in range(num_iterations):
        print(f"\nRandom solution attempt {i+1}/{num_iterations}...")
        
        # Create problem with randomized weights to generate different solutions
        x = pulp.LpVariable.dicts('x', (PEOPLE, task_codes, range(weeks)), 0, 1, pulp.LpBinary)
        prob = pulp.LpProblem(f'TaskRotation_{i}', pulp.LpMinimize)
        
        # Random weights in the objective for variety
        random_weights = {(p, t, w): random.uniform(0.01, 0.05) for p in PEOPLE for t in task_codes for w in range(weeks)}
        prob += pulp.lpSum(random_weights[(p, t, w)] * x[p][t][w] for p in PEOPLE for t in task_codes for w in range(weeks))
        
        # Core constraints
        for p in PEOPLE:
            for w in range(weeks):
                prob += pulp.lpSum(x[p][t][w] for t in task_codes) <= 1

        for t in task_codes:
            for w in range(weeks):
                prob += pulp.lpSum(x[p][t][w] for p in PEOPLE) == 2

        # Link people working together
        y = pulp.LpVariable.dicts('y', (PEOPLE, PEOPLE, range(weeks)), 0, 1, pulp.LpBinary)
        for w in range(weeks):
            for t in task_codes:
                for p1 in PEOPLE:
                    for p2 in PEOPLE:
                        if p1 >= p2:
                            continue
                        prob += y[p1][p2][w] >= x[p1][t][w] + x[p2][t][w] - 1
            for p1 in PEOPLE:
                for p2 in PEOPLE:
                    if p1 >= p2:
                        continue
                    prob += y[p1][p2][w] <= pulp.lpSum(x[p1][t][w] for t in task_codes)
                    prob += y[p1][p2][w] <= pulp.lpSum(x[p2][t][w] for t in task_codes)

        # Perfect task rotation
        task_block = len(task_codes)
        for p in PEOPLE:
            for block_start in range(0, weeks, task_block):
                block_weeks = [w for w in range(block_start, min(block_start + task_block, weeks))]
                for t in task_codes:
                    prob += pulp.lpSum(x[p][t][w] for w in block_weeks) == 1

        # Fair partner distribution
        block_size = len(PEOPLE) - 1
        for p1 in PEOPLE:
            for block_start in range(0, weeks, block_size):
                block_weeks = [w for w in range(block_start, min(block_start + block_size, weeks))]
                for p2 in PEOPLE:
                    if p1 == p2:
                        continue
                    prob += pulp.lpSum(y[min(p1,p2)][max(p1,p2)][w] for w in block_weeks) >= 1
                    prob += pulp.lpSum(y[min(p1,p2)][max(p1,p2)][w] for w in block_weeks) <= 2
        
        # Solve and check the result
        print(f"Solving with {time_limit} second time limit...")
        solver = pulp.PULP_CBC_CMD(msg=False, timeLimit=time_limit)
        prob.solve(solver)
        status = pulp.LpStatus[prob.status]
        print(f"Solution status: {status}")
        
        if status != 'Optimal':
            print("No optimal solution found in this attempt.")
            continue
            
        # Extract solution
        schedule = []
        for w in range(weeks):
            week_assignments = {}
            for t in task_codes:
                assigned = [p for p in PEOPLE if pulp.value(x[p][t][w]) > 0.5]
                if len(assigned) == 2:
                    week_assignments[t] = tuple(assigned)
            schedule.append(week_assignments)
            
        # Check fairness
        min_pair, max_pair, pair_counts = get_pairing_stats(schedule)
        diff = max_pair - min_pair
        print(f"Solution found with diff: {diff} (min: {min_pair}, max: {max_pair})")
        
        if best_diff is None or diff < best_diff:
            best_diff = diff
            best_schedule = schedule
            best_stats = (min_pair, max_pair, pair_counts)
            print(f"This is our new best solution so far! Diff: {diff}")
            
    if best_schedule:
        print(f"\n✨ Best solution has diff = {best_diff} with min pairings = {best_stats[0]}, max pairings = {best_stats[1]}")
        return best_schedule
    else:
        print("❌ No valid solutions found.")
        return None

def print_schedule(schedule, task_codes):
    """Print a nicely formatted version of the schedule"""
    print("\n📅 SCHEDULE 📅")
    print("-" * 40)
    for week, assignments in enumerate(schedule):
        print(f"Week {week+1}:")
        for task in sorted(task_codes):
            if task in assignments:
                pair = assignments[task]
                print(f"  {task}: {pair[0]} ⟷ {pair[1]}")
        print("-" * 20)
        
    # Print statistics
    person_tasks = defaultdict(list)
    person_partners = defaultdict(list)
    for week in schedule:
        for task, pair in week.items():
            p1, p2 = pair
            person_tasks[p1].append(task)
            person_tasks[p2].append(task)
            person_partners[p1].append(p2)
            person_partners[p2].append(p1)
            
    print("\n📊 STATISTICS 📊")
    print("-" * 40)
    print("Task distribution:")
    for person in sorted(PEOPLE):
        task_counts = {t: person_tasks[person].count(t) for t in task_codes}
        print(f"  {person}: {task_counts}")
        
    print("\nPartnership distribution:")
    for person in sorted(PEOPLE):
        partner_counts = {p: person_partners[person].count(p) for p in PEOPLE if p != person}
        print(f"  {person}: {partner_counts}")

def save_to_json(schedule, filename):
    """Save the schedule to a JSON file"""
    with open(filename, 'w') as f:
        json.dump(schedule, f, indent=2)
    print(f"Schedule saved to {filename}")

def hunt_for_solution(task_codes, min_weeks=10, max_weeks=30, max_allowed_diff=2):
    """Try different week counts to find a solution"""
    print(f"Hunting for a solution with {len(task_codes)} tasks...")
    print(f"Will try every week from {min_weeks} to {max_weeks}")
    
    best_schedule = None
    best_diff = None
    best_stats = None
    best_weeks = None
    
    for weeks in range(min_weeks, max_weeks + 1):
        print(f"\nTrying {weeks} weeks...")
        schedule = solve_rotation_schedule(task_codes, weeks, max_allowed_diff=max_allowed_diff)
        if schedule:
            min_pair, max_pair, pair_counts = get_pairing_stats(schedule)
            diff = max_pair - min_pair
            print(f"✨ Found solution with {weeks} weeks! Pairing min: {min_pair}, max: {max_pair}, diff: {diff}")
            if best_diff is None or diff < best_diff:
                best_diff = diff
                best_schedule = schedule
                best_stats = (min_pair, max_pair, pair_counts)
                best_weeks = weeks
                
    if best_schedule:
        print(f"\nBest solution found: weeks = {best_weeks}, min pairings = {best_stats[0]}, max pairings = {best_stats[1]}, diff = {best_diff}")
        return best_weeks, best_schedule
        
    print(f"❌ No fair solution found with max-min diff <= {max_allowed_diff} in the specified range")
    return None, None

if __name__ == "__main__":
    # Task definitions
    kitchen_tasks = ["K1", "K2", "K3"]  # K3 is Cleaning (includes cleaning the cat's box)
    clothing_tasks = ["C1", "C2", "C3"]
    cat_tasks = ["G1", "G2"]
    test3_tasks = ["T1", "T2", "T3"]
    test4_tasks = ["T1", "T2", "T3", "T4"]
    test5_tasks = ["T1", "T2", "T3", "T4", "T5"]
    test6_tasks = ["T1", "T2", "T3", "T4", "T5", "T6"]
    max_allowed_diff = 2
    
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="Task rotation scheduler")
    parser.add_argument("category", nargs="?", default="kitchen", 
                       choices=["kitchen", "clothing", "cats", "test3", "test4", "test5", "test6"],
                       help="Category of tasks to schedule")
    parser.add_argument("weeks", nargs="?", type=int, help="Number of weeks (optional)")
    parser.add_argument("--randomize", "-r", action="store_true", 
                       help="Use randomized solver to find multiple solutions")
    parser.add_argument("--iterations", "-i", type=int, default=5,
                       help="Number of random iterations to try (default: 5)")
    args = parser.parse_args()
    
    # Select tasks based on category
    if args.category == "kitchen":
        tasks = kitchen_tasks
        default_weeks = 18  # Default to 18 weeks for kitchen
    elif args.category == "clothing":
        tasks = clothing_tasks
        default_weeks = None
    elif args.category == "cats":
        tasks = cat_tasks
        default_weeks = None
    elif args.category == "test3":
        tasks = test3_tasks
        default_weeks = None
    elif args.category == "test4":
        tasks = test4_tasks
        default_weeks = None
    elif args.category == "test5":
        tasks = test5_tasks
        default_weeks = None
    elif args.category == "test6":
        tasks = test6_tasks
        default_weeks = None
    
    # Determine number of weeks
    weeks = args.weeks or default_weeks
    
    # Execution path based on arguments
    if args.randomize:
        print(f"Using randomized solver for {args.category} with {args.iterations} iterations...")
        if not weeks:
            print("You must specify the number of weeks when using randomized solver.")
            sys.exit(1)
            
        random_schedule = solve_with_randomness(tasks, weeks=weeks, num_iterations=args.iterations)
        if random_schedule:
            print_schedule(random_schedule, tasks)
            save_to_json(random_schedule, f"{tasks[0].lower()}_rotation.json")
        else:
            print("❌ No solution found with randomized solver!")
    elif weeks:
        schedule = solve_rotation_schedule(tasks, weeks, max_allowed_diff=max_allowed_diff)
        if schedule:
            min_pair, max_pair, _ = get_pairing_stats(schedule)
            diff = max_pair - min_pair
            if diff <= max_allowed_diff:
                print_schedule(schedule, tasks)
                save_to_json(schedule, f"{tasks[0].lower()}_rotation.json")
            else:
                print(f"❌ No solution found with max-min diff <= {max_allowed_diff}!")
        else:
            print("❌ No solution found!")
    else:
        weeks, schedule = hunt_for_solution(tasks, max_allowed_diff=max_allowed_diff)
        if schedule:
            print_schedule(schedule, tasks)
            save_to_json(schedule, f"{tasks[0].lower()}_rotation.json")
        else:
            print("❌ No solution found!") 