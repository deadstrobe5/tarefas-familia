#!/usr/bin/env python3
"""Task definitions module for rotation scheduler"""
from colorama import Fore

# People definitions
PEOPLE = ['A', 'C', 'M', 'P', 'D', 'H']

PEOPLE_SYMBOLS = {
    'A': '👦',  # Afonso
    'C': '👧',  # Catarina
    'M': '👩',  # Madalena 
    'P': '👱‍♀️',  # Paula
    'D': '🧓',  # Deolinda
    'H': '🧔'   # Herculano
}

PEOPLE_DESCRIPTIONS = {
    'A': 'Afonso',
    'C': 'Catarina', 
    'M': 'Madalena',
    'P': 'Paula',
    'D': 'Deolinda',
    'H': 'Herculano'
}

# Task categories
CATEGORIES = {
    "kitchen": "🍽️ Cozinha",
    "clothing": "👕 Roupa",
    "cats": "🐱 Gatos"
}

# Task class definition
class Task:
    def __init__(self, code, symbol, color, description, short_desc=None, category="kitchen"):
        self.code = code
        self.symbol = symbol
        self.color = color
        self.description = description
        self.short_desc = short_desc or code
        self.category = category

# Task definitions
TASKS = [
    # Kitchen tasks
    Task('K1', '🍽️', Fore.GREEN, 'Lavar a loiça durante toda a semana', 'Lavar', category="kitchen"),
    Task('K2', '🧺', Fore.BLUE, 'Arrumar a loiça + Pôr a mesa durante toda a semana', 'Arrumar', category="kitchen"),
    Task('K3', '🧹', Fore.CYAN, 'Limpar a cozinha e a caixa dos gatos durante toda a semana', 'Limpar', category="kitchen"),
    
    # Clothing tasks
    Task('C1', '👕', Fore.YELLOW, 'Lavar a roupa durante toda a semana', 'Lavar', category="clothing"),
    Task('C2', '🧺', Fore.CYAN, 'Estender a roupa durante toda a semana', 'Estender', category="clothing"),
    Task('C3', '🧷', Fore.MAGENTA, 'Dobrar e guardar a roupa durante toda a semana', 'Dobrar', category="clothing"),
    
    # Cat care tasks
    Task('G1', '🐱', Fore.RED, 'Alimentar os gatos durante toda a semana', 'Alimentar', category="cats"),
    Task('G2', '🧹', Fore.GREEN, 'Limpar a caixa de areia durante toda a semana', 'Limpar', category="cats"),
]

# CSS colors for HTML output
TASK_CSS_COLORS = {
    'K1': '#0a7d36',  # darker green
    'K2': '#0e5394',  # darker blue
    'K3': '#008080',  # teal for cleaning
    'C1': '#996600',  # dark yellow
    'C2': '#006666',  # dark cyan
    'C3': '#660066',  # dark magenta
    'G1': '#990000',  # dark red
    'G2': '#004d00',  # dark green
}

# Map legacy codes to new ones
LEGACY_CODE_MAP = {'C1': 'K1', 'C2': 'K2'}

# Default days
DEFAULT_DAYS = 15

def get_tasks_by_category(category=None):
    """Get all tasks in a specific category, or all tasks if category is None"""
    if category is None:
        return TASKS
    return [task for task in TASKS if task.category == category]

def get_task_by_code(code):
    """Get a task object by its code, with backward compatibility for old codes"""
    if code in LEGACY_CODE_MAP:
        code = LEGACY_CODE_MAP[code]
        
    for task in TASKS:
        if task.code == code:
            return task
    raise ValueError(f"Task code {code} not found!")

def create_task_collections(category=None):
    """Create helper collections for task attributes by category"""
    tasks = get_tasks_by_category(category)
    return {
        'TASK_CODES': [t.code for t in tasks],
        'TASK_SYMBOLS': {t.code: t.symbol for t in tasks},
        'TASK_COLORS': {t.code: t.color for t in tasks},
        'TASK_DESCRIPTIONS': {t.code: t.description for t in tasks},
        'TASK_SHORT_DESCRIPTIONS': {t.code: t.short_desc for t in tasks},
        'TASK_CSS_COLORS': TASK_CSS_COLORS
    }

# Default kitchen task collections for backward compatibility
collections = create_task_collections("kitchen")
TASK_CODES = collections['TASK_CODES']
TASK_SYMBOLS = collections['TASK_SYMBOLS']
TASK_COLORS = collections['TASK_COLORS']
TASK_DESCRIPTIONS = collections['TASK_DESCRIPTIONS']
TASK_SHORT_DESCRIPTIONS = collections['TASK_SHORT_DESCRIPTIONS'] 