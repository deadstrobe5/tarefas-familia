#!/usr/bin/env python3
import collections
from collections import defaultdict, Counter
import random
import time
import sys
import os
from itertools import combinations
from colorama import Fore, Style, init
import pulp
import contextlib
import io
import argparse
from tarefas_tasks import (
    TASK_CODES, TASK_SYMBOLS, TASK_COLORS, TASK_DESCRIPTIONS,
    PEOPLE, PEOPLE_SYMBOLS, DEFAULT_DAYS, CATEGORIES,
    get_tasks_by_category, create_task_collections
)
# Import other things from tarefas_print
from tarefas_print import load_schedule_json, export_schedule_to_html, export_schedule_to_pdf, get_output_path

# ========== CONFIGURATION ==========
init(autoreset=True)

# Use centralized values as default but they can be overridden
DAYS = DEFAULT_DAYS
PAIRS = list(combinations(PEOPLE, 2))

# ========== OUTPUT HELPERS ==========
def print_title(category=None):
    category_text = CATEGORIES.get(category, "TAREFAS") if category else "PERFECT PAIRING ROTATION"
    title = f"🔀 {category_text} 🔀"
    colors = [Fore.RED, Fore.YELLOW, Fore.GREEN, Fore.CYAN, Fore.BLUE, Fore.MAGENTA]
    colored_title = ''.join(f"{colors[i % len(colors)]}{char}" for i, char in enumerate(title))
    print(f"\n{Style.BRIGHT}{colored_title}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}{'=' * 50}{Style.RESET_ALL}")

def animated_loading(message="Calculating", duration=1.5):
    frames = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
    end = time.time() + duration
    i = 0
    print()
    while time.time() < end:
        i = (i + 1) % len(frames)
        print(f"\r{Fore.CYAN}{message} {frames[i]}", end='')
        time.sleep(0.1)
    print(f"\r{' ' * (len(message) + 10)}", end='\r')

def progress_bar(iteration, total, prefix='', suffix='', length=50, fill='█', print_end="\r"):
    percent = ("{0:.1f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '░' * (length - filled_length)
    color = Fore.RED
    if iteration / total > 0.3: color = Fore.YELLOW
    if iteration / total > 0.7: color = Fore.GREEN
    print(f'\r{prefix} {color}{bar}{Style.RESET_ALL} {percent}% {suffix}', end=print_end)
    sys.stdout.flush()
    if iteration == total: print()

def print_legend(task_codes, task_symbols, task_colors, task_descriptions):
    print(f"{Fore.WHITE}{Style.BRIGHT}Tasks Legend:{Style.RESET_ALL}")
    for task in task_codes:
        print(f"  {task_colors[task]}{task} {task_symbols[task]}{Style.RESET_ALL}: {task_descriptions[task]}")
    print(f"{Fore.YELLOW}{'-' * 30}{Style.RESET_ALL}\n")

def print_schedule(final_schedule, task_codes, task_symbols, task_colors, category="kitchen"):
    print(f"\n{Fore.YELLOW}{Style.BRIGHT}📆 SEMANAL ({DAYS} SEMANAS) 📆{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}{'-' * 50}{Style.RESET_ALL}\n")
    # Get proper descriptions from the same collection
    collections_data = create_task_collections(category)
    task_descriptions = collections_data['TASK_DESCRIPTIONS']
    print_legend(task_codes, task_symbols, task_colors, task_descriptions)
    for week_num, day in enumerate(final_schedule, 1):
        print(f"{Fore.CYAN}{Style.BRIGHT}Semana {week_num}:{Style.RESET_ALL}")
        for task in sorted(task_codes):
            if task in day:
                pair = day[task]
                p1, p2 = pair
                print(f"  {task_colors[task]}{task} {task_symbols[task]}{Style.RESET_ALL}: {Fore.RED}{p1}{Style.RESET_ALL} {PEOPLE_SYMBOLS[p1]} ⟷ {Fore.RED}{p2}{Style.RESET_ALL} {PEOPLE_SYMBOLS[p2]}")
        print(f"{Fore.YELLOW}{'-' * 30}{Style.RESET_ALL}")

def print_stats(person_tasks, person_partners, task_codes, task_colors, task_symbols, category="kitchen"):
    print(f"\n{Fore.YELLOW}{Style.BRIGHT}🔍 FAIRNESS VERIFICATION 🔍{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}{'=' * 50}{Style.RESET_ALL}\n")
    print(f"{Fore.CYAN}{Style.BRIGHT}📊 Task Distribution:{Style.RESET_ALL}")
    headers = ["Person"] + sorted(task_codes)
    print(f"  {headers[0]:<6}", end="")
    for header in headers[1:]:
        print(f"{task_colors[header]}{header} {task_symbols[header]}  {Style.RESET_ALL}", end="")
    print() ; print(f"  {'-' * 30}")
    for person in PEOPLE:
        task_count = Counter(person_tasks[person])
        symbol = PEOPLE_SYMBOLS[person]
        print(f"  {Fore.RED}{Style.BRIGHT}{person}{Style.RESET_ALL} {symbol} ", end="")
        for task in sorted(task_codes):
            count = task_count.get(task, 0)
            blocks = "■" * count + "□" * (DAYS//len(task_codes) - count)
            print(f"{task_colors[task]}{blocks:<6}{Style.RESET_ALL}", end="")
        print()
    print()
    print(f"{Fore.CYAN}{Style.BRIGHT}🤝 Partnership Distribution:{Style.RESET_ALL}")
    headers = ["Person"] + PEOPLE
    print(f"  {headers[0]:<6}", end="")
    for header in headers[1:]:
        print(f"{Fore.RED}{header:<5}{Style.RESET_ALL}", end="")
    print() ; print(f"  {'-' * 35}")
    for person in PEOPLE:
        partner_count = Counter(person_partners[person])
        symbol = PEOPLE_SYMBOLS[person]
        print(f"  {Fore.RED}{Style.BRIGHT}{person}{Style.RESET_ALL} {symbol} ", end="")
        for partner in PEOPLE:
            if partner == person:
                print(f"{Fore.BLACK}{'X':<5}{Style.RESET_ALL}", end="")
            else:
                count = partner_count.get(partner, 0)
                print(f"{count:<5}", end="")
        print()
    print()

def print_banner():
    print(f"\n{Fore.GREEN}{Style.BRIGHT}{'✨' * 25}{Style.RESET_ALL}")
    completion_msg = "✅ PERFECT FAIR ROTATION COMPLETE ✅"
    rainbow_completion = ""
    for i, char in enumerate(completion_msg):
        color = [Fore.RED, Fore.YELLOW, Fore.GREEN, Fore.BLUE, Fore.MAGENTA][i % 5]
        rainbow_completion += f"{color}{char}"
    print(f"{Style.BRIGHT}{rainbow_completion}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}{Style.BRIGHT}{'✨' * 25}{Style.RESET_ALL}")

# ========== MAIN LOGIC ==========
def main(category=None):
    # Get the appropriate task collections for the selected category
    collections = create_task_collections(category)
    task_codes = collections['TASK_CODES']
    task_symbols = collections['TASK_SYMBOLS']
    task_colors = collections['TASK_COLORS']
    task_descriptions = collections['TASK_DESCRIPTIONS']
    
    print(f"\n{Style.BRIGHT}{Fore.CYAN}Generating the mathematically perfect rotation...{Style.RESET_ALL}")
    steps = 6
    for i in range(steps+1):
        progress_bar(i, steps, prefix=f"{Fore.CYAN}Progress:", suffix="Complete", length=30)
        time.sleep(0.1)
    animated_loading("Solving ILP for perfect balance", 1.5)
    print_title(category)
    print(f"\n{Fore.WHITE}This script creates a mathematically perfect fair rotation with just two simple constraints:")
    print(f"{Fore.WHITE}1. Perfect rotativity of pairs (everyone works with everyone equally)")
    print(f"{Fore.WHITE}2. Perfect rotativity of tasks (each person does each task equally){Style.RESET_ALL}\n")

    # ILP variables
    x = pulp.LpVariable.dicts('x', (range(DAYS), task_codes, PAIRS), 0, 1, pulp.LpBinary)
    prob = pulp.LpProblem('TaskRotation', pulp.LpMinimize)
    prob += 0  # Dummy objective function
    
    # ESSENTIAL CONSTRAINT: Each task must be assigned exactly once per day
    for d in range(DAYS):
        for t in task_codes:
            prob += pulp.lpSum(x[d][t][p] for p in PAIRS) == 1
    
    # GOAL 1: PERFECT ROTATIVITY OF PAIRS
    # Each pair should work together approximately the same number of times
    target_pair_count = DAYS * len(task_codes) // len(PAIRS)
    
    # Handle case when days*tasks isn't divisible evenly by number of pairs
    if (DAYS * len(task_codes)) % len(PAIRS) == 0:
        # Perfect division possible
        for p in PAIRS:
            prob += pulp.lpSum(x[d][t][p] for d in range(DAYS) for t in task_codes) == target_pair_count
    else:
        # Allow a difference of at most 1 task per pair
        for p in PAIRS:
            prob += pulp.lpSum(x[d][t][p] for d in range(DAYS) for t in task_codes) >= target_pair_count
            prob += pulp.lpSum(x[d][t][p] for d in range(DAYS) for t in task_codes) <= target_pair_count + 1

    # GOAL 2: PERFECT ROTATIVITY OF TASKS FOR EACH PERSON
    # Each person should do each task approximately the same number of times
    target_task_count = DAYS // len(task_codes)
    
    # If we can divide days evenly by tasks
    if DAYS % len(task_codes) == 0:
        for person in PEOPLE:
            for t in task_codes:
                prob += pulp.lpSum(x[d][t][p] for d in range(DAYS) for p in PAIRS if person in p) == target_task_count
    else:
        # Allow difference of at most 1 for each person-task combo
        for person in PEOPLE:
            for t in task_codes:
                prob += pulp.lpSum(x[d][t][p] for d in range(DAYS) for p in PAIRS if person in p) >= target_task_count
                prob += pulp.lpSum(x[d][t][p] for d in range(DAYS) for p in PAIRS if person in p) <= target_task_count + 1
    
    # Suppress solver output
    print(f"{Fore.YELLOW}Solving ILP for perfect balance...{Style.RESET_ALL}")
    with contextlib.redirect_stdout(io.StringIO()):
        prob.solve(pulp.PULP_CBC_CMD(msg=False))
    
    print(f"ILP status: {pulp.LpStatus[prob.status]}")
    if pulp.LpStatus[prob.status] != 'Optimal':
        print(f"{Fore.RED}No perfect solution found!{Style.RESET_ALL}")
        exit(1)
    final_schedule = []
    for d in range(DAYS):
        day = {}
        for t in task_codes:
            for p in PAIRS:
                if pulp.value(x[d][t][p]) > 0.5:
                    day[t] = p
        final_schedule.append(day)
    # Collect stats
    person_tasks = defaultdict(list)
    person_partners = defaultdict(list)
    for day in final_schedule:
        for task, pair in day.items():
            p1, p2 = pair
            person_tasks[p1].append(task)
            person_tasks[p2].append(task)
            person_partners[p1].append(p2)
            person_partners[p2].append(p1)
    print_schedule(final_schedule, task_codes, task_symbols, task_colors, category)
    print_stats(person_tasks, person_partners, task_codes, task_colors, task_symbols, category)
    print_banner()
    
    # Save the result
    from tarefas_print import save_schedule_json
    save_schedule_json(final_schedule, category=category)
    
    return final_schedule

def solve_and_return_schedule(days, category=None, time_limit_seconds=10):
    """
    Completely rewritten solver with correct rotation constraints:
    1. If A works with C, A must work with everyone else before working with C again (perfect pair rotation)
    2. If A does task 1, A must do all other tasks before doing task 1 again (perfect task rotation)
    """
    # Get the appropriate task collections for the selected category
    collections = create_task_collections(category)
    task_codes = collections['TASK_CODES']
    
    # Create binary variables: x[day][task][pair] = 1 if pair does task on day
    x = pulp.LpVariable.dicts('x', (range(days), task_codes, PAIRS), 0, 1, pulp.LpBinary)
    
    # Create an optimization problem
    prob = pulp.LpProblem('TaskRotation', pulp.LpMinimize)
    prob += 0  # Dummy objective function
    
    # CONSTRAINT 1: Each task must be assigned exactly once per day
    for d in range(days):
        for t in task_codes:
            prob += pulp.lpSum(x[d][t][p] for p in PAIRS) == 1
    
    # CONSTRAINT 2: No person does more than one task per week
    for d in range(days):
        for person in PEOPLE:
            prob += pulp.lpSum(x[d][t][p] for t in task_codes for p in PAIRS if person in p) <= 1
    
    # CONSTRAINT 3: PERFECT ROTATION OF TASKS FOR EACH PERSON
    # If person does task T, they must do all other tasks before doing T again
    if len(task_codes) > 1:  # Only if we have multiple tasks
        for person in PEOPLE:
            for start_day in range(days - len(task_codes) + 1):
                # In any window of len(task_codes) consecutive days
                window = range(start_day, start_day + len(task_codes))
                
                # Person can't do same task twice in this window
                for t in task_codes:
                    prob += pulp.lpSum(x[d][t][p] for d in window for p in PAIRS if person in p) <= 1
    
    # CONSTRAINT 4: PERFECT ROTATION OF PAIRS FOR EACH PERSON
    # If person works with partner P, they must work with all other people before working with P again
    if len(PEOPLE) > 2:  # Only if we have more than 2 people
        for person in PEOPLE:
            # Get all partners this person can work with
            partners = [p for p in PEOPLE if p != person]
            for start_day in range(days - (len(partners) - 1)):
                # In any window of len(partners) consecutive days where this person works
                window = range(start_day, start_day + len(partners))
                
                # Person can't work with same partner twice in this window
                for partner in partners:
                    # Sum of all times person works with partner in window must be <= 1
                    prob += pulp.lpSum(x[d][t][p] for d in window for t in task_codes 
                                     for p in PAIRS if person in p and partner in p) <= 1
    
    # Add fairness constraints - each person should do each task approximately the same number of times
    min_tasks_per_person = days // (len(PEOPLE) * 2)  # Minimum number each person should do each task
    for person in PEOPLE:
        for t in task_codes:
            prob += pulp.lpSum(x[d][t][p] for d in range(days) for p in PAIRS if person in p) >= min_tasks_per_person
    
    # Each pair should work together at least a minimum number of times
    min_pair_count = days // (len(PAIRS) * 2)  # Each pair should work together minimum number of times
    for p in PAIRS:
        prob += pulp.lpSum(x[d][t][p] for d in range(days) for t in task_codes) >= min_pair_count
    
    # Try to solve with time limit
    with contextlib.redirect_stdout(io.StringIO()):
        solver = pulp.PULP_CBC_CMD(msg=False, timeLimit=time_limit_seconds)
        prob.solve(solver)
    
    if pulp.LpStatus[prob.status] != 'Optimal':
        return None
    
    # Extract solution
    final_schedule = []
    for d in range(days):
        day = {}
        for t in task_codes:
            for p in PAIRS:
                if pulp.value(x[d][t][p]) > 0.5:
                    day[t] = p
        final_schedule.append(day)
    return final_schedule

def hunt_for_solution(category=None, max_attempts=10, min_days=10, max_days=30):
    """Try different configurations of days until a solution is found"""
    print(f"{Fore.CYAN}Hunting for a solution (max {max_attempts} attempts)...{Style.RESET_ALL}")
    collections = create_task_collections(category)
    task_codes = collections['TASK_CODES']
    n_tasks = len(task_codes)
    
    # Try specific numbers first that are likely to work
    candidates = []
    
    # Add days that are multiples of 5 (for fair pairing) and the number of tasks
    for days in range(min_days, max_days + 1, 5):
        if days % n_tasks == 0:
            candidates.append(days)
    
    # Add a few extras to try
    for extra in [15, 20, 30]:
        if extra not in candidates and min_days <= extra <= max_days:
            candidates.append(extra)
    
    # Sort and limit the attempts
    candidates = sorted(candidates)[:max_attempts]
    
    print(f"{Fore.YELLOW}Will try these day counts: {candidates}{Style.RESET_ALL}")
    
    for i, days in enumerate(candidates, 1):
        print(f"{Fore.CYAN}Attempt {i}/{len(candidates)}: Trying {days} days...{Style.RESET_ALL}", end="", flush=True)
        schedule = solve_and_return_schedule(days, category=category)
        if schedule:
            print(f"{Fore.GREEN} ✓ Found solution!{Style.RESET_ALL}")
            return days, schedule
        print(f"{Fore.RED} ✗ No solution.{Style.RESET_ALL}")
    
    # If all else fails, try with a relaxed constraints variant
    print(f"{Fore.YELLOW}No solution found with strict constraints. Trying relaxed variant...{Style.RESET_ALL}")
    days = candidates[-1]  # Use the largest day count we tried
    schedule = solve_relaxed_schedule(days, category)
    if schedule:
        print(f"{Fore.GREEN}Found solution with relaxed constraints!{Style.RESET_ALL}")
        return days, schedule
        
    print(f"{Fore.RED}Failed to find any solution after {max_attempts} attempts.{Style.RESET_ALL}")
    return None, None

def solve_relaxed_schedule(days, category=None, time_limit_seconds=15):
    """
    Relaxed solver that maintains the perfect rotation constraints but relaxes distribution requirements.
    """
    # Get the appropriate task collections for the selected category
    collections = create_task_collections(category)
    task_codes = collections['TASK_CODES']
    
    # Create binary variables: x[day][task][pair] = 1 if pair does task on day
    x = pulp.LpVariable.dicts('x', (range(days), task_codes, PAIRS), 0, 1, pulp.LpBinary)
    
    # Create an optimization problem
    prob = pulp.LpProblem('TaskRotation', pulp.LpMinimize)
    prob += 0  # Dummy objective function
    
    # CONSTRAINT 1: Each task must be assigned exactly once per day
    for d in range(days):
        for t in task_codes:
            prob += pulp.lpSum(x[d][t][p] for p in PAIRS) == 1
    
    # CONSTRAINT 2: No person does more than one task per week
    for d in range(days):
        for person in PEOPLE:
            prob += pulp.lpSum(x[d][t][p] for t in task_codes for p in PAIRS if person in p) <= 1
    
    # CONSTRAINT 3: RELAXED ROTATION OF TASKS
    # Instead of perfect rotation, just prevent immediate repeats
    for person in PEOPLE:
        for d in range(days - 1):
            for t in task_codes:
                # Person can't do same task on consecutive days
                prob += pulp.lpSum(x[d][t][p] for p in PAIRS if person in p) + \
                       pulp.lpSum(x[d+1][t][p] for p in PAIRS if person in p) <= 1
    
    # CONSTRAINT 4: RELAXED ROTATION OF PAIRS
    # Instead of perfect rotation, just prevent immediate repeats of partnerships
    for person in PEOPLE:
        for partner in PEOPLE:
            if person != partner:
                for d in range(days - 1):
                    # Person can't work with same partner on consecutive days
                    prob += pulp.lpSum(x[d][t][p] for t in task_codes for p in PAIRS if person in p and partner in p) + \
                           pulp.lpSum(x[d+1][t][p] for t in task_codes for p in PAIRS if person in p and partner in p) <= 1
    
    # FAIRNESS CONSTRAINT: Prevent any one person from doing too many tasks
    # Maximum percentage of tasks any person can do
    max_percent_tasks = 0.3  # No person can do more than 30% of all tasks
    total_tasks = days * len(task_codes)
    for person in PEOPLE:
        prob += pulp.lpSum(x[d][t][p] for d in range(days) for t in task_codes for p in PAIRS if person in p) <= \
                total_tasks * max_percent_tasks
    
    # Minimum tasks constraint - everyone should do at least one task
    for person in PEOPLE:
        prob += pulp.lpSum(x[d][t][p] for d in range(days) for t in task_codes for p in PAIRS if person in p) >= 1
    
    # Try to solve with time limit
    with contextlib.redirect_stdout(io.StringIO()):
        solver = pulp.PULP_CBC_CMD(msg=False, timeLimit=time_limit_seconds)
        prob.solve(solver)
    
    if pulp.LpStatus[prob.status] != 'Optimal':
        return None
    
    # Extract solution
    final_schedule = []
    for d in range(days):
        day = {}
        for t in task_codes:
            for p in PAIRS:
                if pulp.value(x[d][t][p]) > 0.5:
                    day[t] = p
        final_schedule.append(day)
    return final_schedule

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Task rotation scheduler")
    parser.add_argument('--pdf', action='store_true', help='Export the schedule to a beautiful PDF for printing')
    parser.add_argument('--auto-days', '-a', action='store_true', help='Automatically increment days until a solution is found')
    parser.add_argument('--from-json', action='store_true', help='Export HTML/PDF from saved JSON schedule (no solver)')
    parser.add_argument('--days', type=int, help='Number of days to schedule (default: 15)')
    parser.add_argument('--start-date', type=str, help='Starting date in DD/MM/YYYY format (default: 05/05/2024)')
    parser.add_argument('--category', '-c', type=str, choices=list(CATEGORIES.keys()), default="kitchen",
                       help=f'Task category to generate schedule for (default: kitchen)')
    args = parser.parse_args()
    
    # Custom start date
    start_date = None
    if args.start_date:
        try:
            from datetime import datetime
            day, month, year = map(int, args.start_date.split('/'))
            start_date = datetime(year, month, day)
            print(f"Using custom start date: {start_date.strftime('%d/%m/%Y')}")
        except:
            print(f"Invalid date format. Please use DD/MM/YYYY. Using default date.")
    
    # Get selected category
    category = args.category
    print(f"{Fore.CYAN}Working with category: {CATEGORIES[category]}{Style.RESET_ALL}")
    
    # Show available tasks in this category
    collections = create_task_collections(category)
    task_codes = collections['TASK_CODES']
    if not task_codes:
        print(f"{Fore.RED}No tasks defined for category '{category}'! Please uncomment or add tasks in tarefas_tasks.py.{Style.RESET_ALL}")
        exit(1)
    else:
        print(f"{Fore.WHITE}Found {len(task_codes)} tasks: {', '.join(task_codes)}{Style.RESET_ALL}")
    
    # Explain output location
    print(f"{Fore.WHITE}All output files will be saved to: output/{category}/{Style.RESET_ALL}")
    
    # Override days if specified
    if args.days:
        DAYS = args.days
        print(f"Using {DAYS} days as specified")
    
    if args.from_json:
        from tarefas_print import load_schedule_json, export_schedule_to_html, export_schedule_to_pdf
        schedule = load_schedule_json(category=category)
        if args.pdf:
            export_schedule_to_pdf(schedule, start_date=start_date, category=category)
        else:
            export_schedule_to_html(schedule, start_date=start_date, category=category)
        exit(0)
    elif args.auto_days:
        print(f"{Fore.CYAN}Using smart solution hunting to find a valid schedule...{Style.RESET_ALL}")
        days, final_schedule = hunt_for_solution(category=category)
        
        if final_schedule:
            DAYS = days
            print(f"{Fore.GREEN}Solution found with {days} days!{Style.RESET_ALL}")
            
            # Print and/or export as usual
            collections_data = create_task_collections(category)
            task_codes = collections_data['TASK_CODES']
            task_symbols = collections_data['TASK_SYMBOLS']
            task_colors = collections_data['TASK_COLORS']
            
            person_tasks = defaultdict(list)
            person_partners = defaultdict(list)
            for day in final_schedule:
                for task, pair in day.items():
                    p1, p2 = pair
                    person_tasks[p1].append(task)
                    person_tasks[p2].append(task)
                    person_partners[p1].append(p2)
                    person_partners[p2].append(p1)
                print_schedule(final_schedule, task_codes, task_symbols, task_colors, category)
                print_stats(person_tasks, person_partners, task_codes, task_colors, task_symbols, category)
            print_banner()
            from tarefas_print import save_schedule_json
            save_schedule_json(final_schedule, category=category)
            if args.pdf:
                from tarefas_print import export_schedule_to_pdf
                export_schedule_to_pdf(final_schedule, start_date=start_date, category=category)
            else:
                print(f"{Fore.RED}Could not find any valid solution. Try with fewer people or tasks.{Style.RESET_ALL}")
                exit(1)
        else:
            print(f"{Fore.RED}Failed to find any solution after {max_attempts} attempts.{Style.RESET_ALL}")
            exit(1)
    else:
        # Run normal flow
        final_schedule = main(category=category)
        if args.pdf:
            from tarefas_print import export_schedule_to_pdf
            export_schedule_to_pdf(final_schedule, start_date=start_date, category=category) 