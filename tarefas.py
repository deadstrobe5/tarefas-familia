#!/usr/bin/env python3
import collections
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
    PEOPLE, PEOPLE_SYMBOLS, DEFAULT_DAYS
)

# ========== CONFIGURATION ==========
init(autoreset=True)

# Use centralized values as default but they can be overridden
DAYS = DEFAULT_DAYS
PAIRS = list(combinations(PEOPLE, 2))

# ========== OUTPUT HELPERS ==========
def print_title():
    title = "🔀 PERFECT PAIRING ROTATION 🔀"
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

def print_legend():
    print(f"{Fore.WHITE}{Style.BRIGHT}Tasks Legend:{Style.RESET_ALL}")
    for task in TASK_CODES:
        print(f"  {TASK_COLORS[task]}{task} {TASK_SYMBOLS[task]}{Style.RESET_ALL}: {TASK_DESCRIPTIONS[task]}")
    print(f"{Fore.YELLOW}{'-' * 30}{Style.RESET_ALL}\n")

def print_schedule(final_schedule):
    print(f"\n{Fore.YELLOW}{Style.BRIGHT}📆 DAILY ASSIGNMENTS ({DAYS} DAYS) 📆{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}{'-' * 50}{Style.RESET_ALL}\n")
    print_legend()
    for day_num, day in enumerate(final_schedule, 1):
        print(f"{Fore.CYAN}{Style.BRIGHT}Day {day_num}:{Style.RESET_ALL}")
        for task in sorted(TASK_CODES):
            if task in day:
                pair = day[task]
                p1, p2 = pair
                print(f"  {TASK_COLORS[task]}{task} {TASK_SYMBOLS[task]}{Style.RESET_ALL}: {Fore.RED}{p1}{Style.RESET_ALL} {PEOPLE_SYMBOLS[p1]} ⟷ {Fore.RED}{p2}{Style.RESET_ALL} {PEOPLE_SYMBOLS[p2]}")
        print(f"{Fore.YELLOW}{'-' * 30}{Style.RESET_ALL}")

def print_stats(person_tasks, person_partners):
    print(f"\n{Fore.YELLOW}{Style.BRIGHT}🔍 FAIRNESS VERIFICATION 🔍{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}{'=' * 50}{Style.RESET_ALL}\n")
    print(f"{Fore.CYAN}{Style.BRIGHT}📊 Task Distribution:{Style.RESET_ALL}")
    headers = ["Person"] + sorted(TASK_CODES)
    print(f"  {headers[0]:<6}", end="")
    for header in headers[1:]:
        print(f"{TASK_COLORS[header]}{header} {TASK_SYMBOLS[header]}  {Style.RESET_ALL}", end="")
    print() ; print(f"  {'-' * 30}")
    for person in PEOPLE:
        task_count = collections.Counter(person_tasks[person])
        symbol = PEOPLE_SYMBOLS[person]
        print(f"  {Fore.RED}{Style.BRIGHT}{person}{Style.RESET_ALL} {symbol} ", end="")
        for task in sorted(TASK_CODES):
            count = task_count.get(task, 0)
            blocks = "■" * count + "□" * (DAYS//3 - count)
            print(f"{TASK_COLORS[task]}{blocks:<6}{Style.RESET_ALL}", end="")
        print()
    print()
    print(f"{Fore.CYAN}{Style.BRIGHT}🤝 Partnership Distribution:{Style.RESET_ALL}")
    headers = ["Person"] + PEOPLE
    print(f"  {headers[0]:<6}", end="")
    for header in headers[1:]:
        print(f"{Fore.RED}{header:<5}{Style.RESET_ALL}", end="")
    print() ; print(f"  {'-' * 35}")
    for person in PEOPLE:
        partner_count = collections.Counter(person_partners[person])
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
def main():
    print(f"\n{Style.BRIGHT}{Fore.CYAN}Generating the mathematically perfect rotation...{Style.RESET_ALL}")
    steps = 6
    for i in range(steps+1):
        progress_bar(i, steps, prefix=f"{Fore.CYAN}Progress:", suffix="Complete", length=30)
        time.sleep(0.1)
    animated_loading("Solving ILP for perfect balance", 1.5)
    print_title()
    print(f"\n{Fore.WHITE}This script creates a mathematically perfect fair rotation using:")
    print(f"{Fore.WHITE}1. Round robin scheduling algorithm with {DAYS} days")
    print(f"{Fore.WHITE}2. Perfect task assignment (each task once per day)")
    print(f"{Fore.WHITE}This guarantees each person works with every other person exactly {DAYS//5} times,")
    print(f"{Fore.WHITE}and each person performs each kitchen task exactly {DAYS//3} times.{Style.RESET_ALL}\n")

    # ILP variables
    x = pulp.LpVariable.dicts('x', (range(DAYS), TASK_CODES, PAIRS), 0, 1, pulp.LpBinary)
    prob = pulp.LpProblem('KitchenRotation', pulp.LpMinimize)
    prob += 0
    for d in range(DAYS):
        for t in TASK_CODES:
            prob += pulp.lpSum(x[d][t][p] for p in PAIRS) == 1
        for p in PAIRS:
            prob += pulp.lpSum(x[d][t][p] for t in TASK_CODES) <= 1
    for p in PAIRS:
        prob += pulp.lpSum(x[d][t][p] for d in range(DAYS) for t in TASK_CODES) == DAYS//5
    for person in PEOPLE:
        for t in TASK_CODES:
            prob += pulp.lpSum(x[d][t][p] for d in range(DAYS) for p in PAIRS if person in p) == DAYS//3
    # NEW CONSTRAINT: No person does more than one task per day
    for d in range(DAYS):
        for person in PEOPLE:
            prob += pulp.lpSum(x[d][t][p] for t in TASK_CODES for p in PAIRS if person in p) <= 1
    # NEW CONSTRAINT: No person does the same task on two consecutive days
    for person in PEOPLE:
        for t in TASK_CODES:
            for d in range(DAYS - 1):
                prob += (
                    pulp.lpSum(x[d][t][p] for p in PAIRS if person in p) +
                    pulp.lpSum(x[d+1][t][p] for p in PAIRS if person in p)
                ) <= 1
    
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
        for t in TASK_CODES:
            for p in PAIRS:
                if pulp.value(x[d][t][p]) > 0.5:
                    day[t] = p
        final_schedule.append(day)
    # Collect stats
    person_tasks = collections.defaultdict(list)
    person_partners = collections.defaultdict(list)
    for day in final_schedule:
        for task, pair in day.items():
            p1, p2 = pair
            person_tasks[p1].append(task)
            person_tasks[p2].append(task)
            person_partners[p1].append(p2)
            person_partners[p2].append(p1)
    print_schedule(final_schedule)
    print_stats(person_tasks, person_partners)
    print_banner()
    
    # Save the result
    from tarefas_print import save_schedule_json
    save_schedule_json(final_schedule)
    
    return final_schedule

def solve_and_return_schedule(days):
    """Solve the ILP problem for the given number of days and return the schedule."""
    x = pulp.LpVariable.dicts('x', (range(days), TASK_CODES, PAIRS), 0, 1, pulp.LpBinary)
    prob = pulp.LpProblem('KitchenRotation', pulp.LpMinimize)
    prob += 0
    for d in range(days):
        for t in TASK_CODES:
            prob += pulp.lpSum(x[d][t][p] for p in PAIRS) == 1
        for p in PAIRS:
            prob += pulp.lpSum(x[d][t][p] for t in TASK_CODES) <= 1
    for p in PAIRS:
        prob += pulp.lpSum(x[d][t][p] for d in range(days) for t in TASK_CODES) == days//5
    for person in PEOPLE:
        for t in TASK_CODES:
            prob += pulp.lpSum(x[d][t][p] for d in range(days) for p in PAIRS if person in p) == days//3
    # NEW CONSTRAINT: No person does more than one task per day
    for d in range(days):
        for person in PEOPLE:
            prob += pulp.lpSum(x[d][t][p] for t in TASK_CODES for p in PAIRS if person in p) <= 1
    # NEW CONSTRAINT: No person does the same task on two consecutive days
    for person in PEOPLE:
        for t in TASK_CODES:
            for d in range(days - 1):
                prob += (
                    pulp.lpSum(x[d][t][p] for p in PAIRS if person in p) +
                    pulp.lpSum(x[d+1][t][p] for p in PAIRS if person in p)
                ) <= 1
    with contextlib.redirect_stdout(io.StringIO()):
        prob.solve(pulp.PULP_CBC_CMD(msg=False))
    if pulp.LpStatus[prob.status] != 'Optimal':
        return None
    final_schedule = []
    for d in range(days):
        day = {}
        for t in TASK_CODES:
            for p in PAIRS:
                if pulp.value(x[d][t][p]) > 0.5:
                    day[t] = p
        final_schedule.append(day)
    return final_schedule

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Kitchen rotation scheduler")
    parser.add_argument('--pdf', action='store_true', help='Export the schedule to a beautiful PDF for printing')
    parser.add_argument('--auto-days', '-a', action='store_true', help='Automatically increment days until a solution is found')
    parser.add_argument('--from-json', action='store_true', help='Export HTML/PDF from saved JSON schedule (no solver)')
    parser.add_argument('--days', type=int, help='Number of days to schedule (default: 15)')
    parser.add_argument('--start-date', type=str, help='Starting date in DD/MM/YYYY format (default: 05/05/2024)')
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
    
    # Override days if specified
    if args.days:
        DAYS = args.days
        print(f"Using {DAYS} days as specified")
    
    if args.from_json:
        from tarefas_print import load_schedule_json, export_schedule_to_html, export_schedule_to_pdf
        schedule = load_schedule_json()
        if args.pdf:
            export_schedule_to_pdf(schedule)
        else:
            export_schedule_to_html(schedule, start_date=start_date)
        exit(0)
    elif args.auto_days:
        days = DAYS
        print(f"{Fore.CYAN}À procura de uma solução...{Style.RESET_ALL}")
        while True:
            if days % 3 != 0 or days % 5 != 0:
                days += 1
                continue
            schedule = solve_and_return_schedule(days)
            if schedule:
                print(f"{Fore.GREEN}Solução encontrada com {days} dias!{Style.RESET_ALL}")
                DAYS = days
                final_schedule = schedule
                break
            days += 1
        # Print and/or export as usual
        person_tasks = collections.defaultdict(list)
        person_partners = collections.defaultdict(list)
        for day in final_schedule:
            for task, pair in day.items():
                p1, p2 = pair
                person_tasks[p1].append(task)
                person_tasks[p2].append(task)
                person_partners[p1].append(p2)
                person_partners[p2].append(p1)
        print_schedule(final_schedule)
        print_stats(person_tasks, person_partners)
        print_banner()
        from tarefas_print import save_schedule_json
        save_schedule_json(final_schedule)
        if args.pdf:
            from tarefas_print import export_schedule_to_pdf
            export_schedule_to_pdf(final_schedule, start_date=start_date)
    else:
        # Run normal flow
        final_schedule = main()
        if args.pdf:
            from tarefas_print import export_schedule_to_pdf
            export_schedule_to_pdf(final_schedule, start_date=start_date) 