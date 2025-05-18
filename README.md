# Task Rotation Scheduler

A fair task rotation scheduler that creates mathematically balanced schedules for household chores and responsibilities.

## Overview

This scheduler solves the problem of creating a fair rotation of tasks among a group of people, ensuring:

1. **Perfect Pair Rotation**: Each person works with every other person an equal number of times (or as close as possible)
2. **Perfect Task Rotation**: Each person performs each task an equal number of times before repeating

The system is designed to be simple, flexible, and efficient. It supports multiple categories of tasks (kitchen, clothing, cats, etc.) and generates pretty HTML/PDF schedules.

## Features

- **Fair distribution** of task loads and partnership pairings
- **Multiple categories** for different types of household responsibilities
- **Mathematically balanced** task assignments
- **HTML and PDF exports** of schedules with week ranges
- **Random solution search** to find the most balanced schedules
- **Command-line interface** for easy use

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/task-rotation-scheduler.git
   cd task-rotation-scheduler
   ```

2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. For PDF generation, you may need additional system packages:
   ```bash
   sudo apt install libpango-1.0-0 libpangocairo-1.0-0 libcairo2
   ```

## Usage

### Running for a Single Category

To generate a schedule for a specific category:

```bash
python3 simple_solver.py kitchen
```

Available categories: `kitchen`, `clothing`, `cats`, `test3`, `test4`, `test5`, `test6`

### Specifying Weeks

```bash
python3 simple_solver.py kitchen 18
```

### Using the Randomized Solver (Recommended)

The randomized solver tries multiple solutions and picks the most balanced one:

```bash
python3 simple_solver.py kitchen --randomize --iterations 100
```

### Generating Prettier PDFs

After generating a schedule with simple_solver.py, you can create a nicely formatted PDF:

```bash
python3 tarefas.py -c kitchen --from-json --pdf
```

### Running All Categories

To process all categories at once:

```bash
python3 run_all.py
```

Options:
- `--solver-only`: Only generate schedules, no PDFs
- `--pdf-only`: Only create PDFs from existing schedules
- `--start-date DD/MM/YYYY`: Set a custom start date (default is May 20, 2024)

## Components

The system consists of these main files:

- **simple_solver.py**: The core solver that creates balanced schedules
- **tarefas_tasks.py**: Task and person definitions
- **tarefas_print.py**: HTML/PDF generation utilities
- **tarefas.py**: Integrates all components with richer features
- **run_all.py**: Utility to run all categories at once

## How It Works

The scheduler uses integer linear programming via the PuLP library to find optimal solutions that satisfy the two main constraints:

1. **Perfect pair rotation**: For each person, if they work with Person X this week, they won't work with Person X again until they've worked with everyone else
2. **Perfect task rotation**: For each person, if they do Task A this week, they won't do Task A again until they've done all other tasks

The randomized solver tries multiple schedule configurations by adding small random weights to the objective function, allowing it to find different solutions and pick the most balanced one (with the smallest difference between minimum and maximum pairing frequencies).

## Customization

You can customize the tasks and people by editing `tarefas_tasks.py`:

- Add/modify tasks in the `TASKS` list
- Change people in the `PEOPLE` list
- Add new categories as needed

## License

This project is released under the MIT License.

## Credits

Developed by Afonso.
Built with PuLP, WeasyPrint, and Colorama. 