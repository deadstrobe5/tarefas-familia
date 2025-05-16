# tarefas_print.py
# Handles exporting the schedule to a beautiful printable format (HTML or PDF).

import json
import webbrowser
import os
import locale
from datetime import datetime, timedelta
from tarefas_tasks import (
    TASK_CODES, TASK_SYMBOLS, TASK_DESCRIPTIONS, TASK_SHORT_DESCRIPTIONS,
    PEOPLE_SYMBOLS
)

# Update to darker/higher contrast colors for better visibility
TASK_CSS_COLORS = {
    'C1': '#0a7d36',  # darker green
    'C2': '#0e5394',  # darker blue
    'C3': '#750a8c',  # darker purple
}

# Set locale to Portuguese
try:
    locale.setlocale(locale.LC_TIME, 'pt_PT.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
    except:
        print("Aviso: Não foi possível configurar locale Português. Os meses estarão em inglês.")

# Month and day translations for Portuguese
MONTH_NAMES = {
    1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr', 
    5: 'Mai', 6: 'Jun', 7: 'Jul', 8: 'Ago',
    9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez'
}

WEEKDAY_NAMES = {
    0: 'Seg', 1: 'Ter', 2: 'Qua', 3: 'Qui', 
    4: 'Sex', 5: 'Sáb', 6: 'Dom'
}

def format_date_pt(date):
    """Format date in Portuguese: '05 Mai (Dom)'"""
    day = date.day
    month = MONTH_NAMES[date.month]
    weekday = WEEKDAY_NAMES[date.weekday()]
    return f"{day:02d} {month} ({weekday})"

def export_schedule_to_html(final_schedule, filename="kitchen_rotation.html", start_date=None):
    """
    Export the schedule to a beautiful HTML file that's ready to print.
    
    Parameters:
    - final_schedule: The schedule data
    - filename: Output HTML filename
    - start_date: Starting date (default: May 5, 2024)
    """
    if start_date is None:
        start_date = datetime(2024, 5, 5)  # May 5, 2024
        
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset=\"UTF-8\">
    <title>Tarefas de Refeição</title>
    <style>
        body {{
            font-family: 'Helvetica', 'Arial', sans-serif;
            line-height: 1.6;
            color: #222;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            background: #f8f9fa;
        }}
        h1 {{
            text-align: center;
            color: #2c3e50;
            padding: 6px;
            margin-bottom: 15px;
            border-bottom: 2px solid #ecf0f1;
            font-size: 2em;
        }}
        .legend {{
            margin: 10px 0;
            border-collapse: collapse;
            width: 100%;
            background: #fff;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 8px #0001;
        }}
        .legend th {{
            background-color: #ffe066;
            text-align: left;
            padding: 8px 6px;
            font-size: 1em;
        }}
        .legend td {{
            padding: 6px;
            border: 1px solid #eee;
            font-size: 0.9em;
        }}
        .task-emoji {{
            font-size: 1.2em;
            margin-right: 5px;
        }}
        .task-title {{
            font-weight: bold;
            font-size: 1.1em;
        }}
        .task-lavar {{ 
            color: {TASK_CSS_COLORS['C1']}; 
            font-weight: bold; 
        }}
        .task-arrumar {{ 
            color: {TASK_CSS_COLORS['C2']}; 
            font-weight: bold; 
        }}
        .task-limpar {{ 
            color: {TASK_CSS_COLORS['C3']}; 
            font-weight: bold; 
        }}
        .schedule {{
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
            background: #fff;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 8px #0001;
            table-layout: fixed;
        }}
        .schedule th {{
            background-color: #1a5fb4;
            color: #fff;
            padding: 14px 8px;
            text-align: center;
            font-size: 1.1em;
            letter-spacing: 1px;
        }}
        .schedule .task-header {{
            display: inline-block;
            padding: 3px 8px;
            border-radius: 4px;
            background-color: rgba(255, 255, 255, 0.15);
            font-weight: bold;
        }}
        .schedule .day-col {{
            background-color: #1a5fb4;
            color: #fff;
            font-weight: bold;
            padding: 6px 4px;
            text-align: center;
            width: 100px;
        }}
        .schedule td {{
            border: 1px solid #eee;
            padding: 8px 4px;
            text-align: center;
            font-size: 0.9em;
            height: 40px;
            vertical-align: middle;
        }}
        .schedule tr:nth-child(even) {{
            background-color: #f4f8fb;
        }}
        .footer {{
            text-align: center;
            margin-top: 30px;
            color: #7f8c8d;
            font-size: 1em;
        }}
        @media print {{
            body {{
                padding: 0;
                margin: 0;
                background: #fff;
                font-size: 95%;
            }}
            h1 {{
                margin-top: 10px;
                margin-bottom: 10px;
                page-break-after: avoid;
            }}
            .schedule {{
                page-break-inside: auto;
                margin: 10px 0;
            }}
            .schedule tr {{
                page-break-inside: avoid;
                page-break-after: auto;
            }}
            .page-break {{
                page-break-after: always;
            }}
            .legend {{
                page-break-inside: avoid;
            }}
            tr {{
                break-inside: avoid;
            }}
        }}
    </style>
</head>
<body>
    <h1>🍽️ TAREFAS DE REFEIÇÃO 🍽️</h1>
    <table class=\"legend\">
        <tr>
            <th>Tarefa</th>
            <th>Descrição</th>
        </tr>
"""
    # Include emoji directly with task name
    for i, code in enumerate(TASK_CODES):
        task_class = f"task-{TASK_SHORT_DESCRIPTIONS[code].lower()}"
        html_content += f"""
        <tr>
            <td><span class="{task_class} task-title"><span class="task-emoji">{TASK_SYMBOLS[code]}</span>{TASK_SHORT_DESCRIPTIONS[code]}</span></td>
            <td>{TASK_DESCRIPTIONS[code]}</td>
        </tr>"""
    html_content += """
    </table>
    <table class=\"schedule\">
        <tr>
            <th>Data</th>
"""
    # Use white text with background color in table headers for better contrast
    for code in TASK_CODES:
        short_desc = TASK_SHORT_DESCRIPTIONS[code]
        html_content += f'            <th><span class="task-header">{TASK_SYMBOLS[code]} {short_desc}</span></th>\n'
    html_content += "        </tr>\n"
    
    # Generate actual calendar dates with Portuguese month names
    for day_num, day in enumerate(final_schedule, 0):
        current_date = start_date + timedelta(days=day_num)
        date_str = format_date_pt(current_date)
        
        # Add page break after day 10, 20, 30, etc.
        page_break_class = ' class="page-break"' if (day_num + 1) % 10 == 0 else ''
        
        html_content += f"        <tr{page_break_class}>\n            <td class=\"day-col\">{date_str}</td>\n"
        for code in TASK_CODES:
            if code in day:
                p1, p2 = day[code]
                html_content += f'            <td>{p1} {PEOPLE_SYMBOLS[p1]} ⟷ {p2} {PEOPLE_SYMBOLS[p2]}</td>\n'
            else:
                html_content += '            <td></td>\n'
        html_content += "        </tr>\n"
    
    # Close the table properly
    html_content += """    </table>
    
    <div class=\"footer\">
        Feito por Afonso ❤️
    </div>
</body>
</html>
"""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"HTML exportado para {filename}")
    print(f"A abrir {filename} no seu navegador.")
    webbrowser.open('file://' + os.path.realpath(filename))

def export_schedule_to_pdf(final_schedule, filename="kitchen_rotation.pdf", start_date=None):
    """
    For PDF export, we'll first create an HTML file and, if possible, convert it to PDF using WeasyPrint.
    """
    html_file = filename.replace('.pdf', '.html')
    export_schedule_to_html(final_schedule, html_file, start_date=start_date)
    try:
        from weasyprint import HTML
        HTML(html_file).write_pdf(filename)
        print(f"PDF exportado para {filename}")
    except ImportError:
        print("[AVISO] WeasyPrint não está instalado! Só foi gerado o HTML. Para PDF perfeito, instala com: pip install weasyprint && sudo apt install libpango-1.0-0 libpangocairo-1.0-0 libcairo2")
        print("Abri o HTML no navegador. Usa Ctrl+P para imprimir ou guardar como PDF (menos bonito).")

def save_schedule_json(final_schedule, filename="kitchen_rotation.json"):
    """Save the schedule to a JSON file for later reuse"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(final_schedule, f, ensure_ascii=False, indent=2)
    print(f"Schedule guardado em {filename}")

def load_schedule_json(filename="kitchen_rotation.json"):
    """Load a schedule from a previously saved JSON file"""
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f) 