# tarefas_tasks.py
# This module centralizes all task and person definitions for the kitchen rotation system

from colorama import Fore

# ========== PEOPLE DEFINITIONS ==========
PEOPLE = ['A', 'C', 'M', 'P', 'D', 'H']

PEOPLE_SYMBOLS = {
    'A': '👦',  # older son
    'C': '👧',  # middle daughter
    'M': '👩',  # younger daughter
    'P': '👱‍♀️',  # Mom (blonde as fuck)
    'D': '🧓',  # grandma (old as hell, but still kicking ass)
    'H': '🧔'   # dad (beard guy, fuck yeah)
}

PEOPLE_DESCRIPTIONS = {
    'A': 'Afonso',
    'C': 'Catarina', 
    'M': 'Madalena',
    'P': 'Paula',
    'D': 'Deolinda',
    'H': 'Herculano'
}

# ========== TASK DEFINITIONS ==========
class Task:
    def __init__(self, code, symbol, color, description, short_desc=None):
        self.code = code
        self.symbol = symbol
        self.color = color
        self.description = description
        self.short_desc = short_desc or code

# Default tasks (can be extended)
TASKS = [
    Task('C1', '🍽️', Fore.GREEN, 'Lavar a loiça', 'Lavar'),
    Task('C2', '🧺', Fore.BLUE, 'Arrumar a loiça + Pôr a mesa', 'Arrumar'),
    Task('C3', '🧹', Fore.MAGENTA, 'Limpar a cozinha (mesa, banca, fogão, migalhas, etc)', 'Limpar'),
]

def get_task_by_code(code):
    """Get a task object by its code"""
    for task in TASKS:
        if task.code == code:
            return task
    raise ValueError(f"Task code {code} not found!")

# Helper collections for easy access
TASK_CODES = [t.code for t in TASKS]
TASK_SYMBOLS = {t.code: t.symbol for t in TASKS}
TASK_COLORS = {t.code: t.color for t in TASKS}
TASK_DESCRIPTIONS = {t.code: t.description for t in TASKS}
TASK_SHORT_DESCRIPTIONS = {t.code: t.short_desc for t in TASKS}

# ========== HTML/CSS COLOR MAPPING ==========
# Map colorama colors to CSS colors
TASK_CSS_COLORS = {
    'C1': '#2ecc71',  # green
    'C2': '#3498db',  # blue
    'C3': '#9b59b6',  # purple
}

# ========== DEFAULT CONFIGURATION ==========
DEFAULT_DAYS = 15  # Default number of days for the rotation 