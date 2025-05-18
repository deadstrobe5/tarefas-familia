#!/usr/bin/env python3
"""Module for exporting schedules to HTML/PDF formats"""

import json
import webbrowser
import os
import locale
from datetime import datetime, timedelta

# Try to use Portuguese locale if available
try:
    locale.setlocale(locale.LC_TIME, 'pt_PT.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
    except:
        print("Warning: Could not set Portuguese locale. Dates will be in English.")

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

def get_output_path(filename, category="kitchen"):
    """Get the full path for an output file in the category directory"""
    # Create output/category directory if it doesn't exist
    output_dir = f"output/{category}"
    os.makedirs(output_dir, exist_ok=True)
    
    # Return full path
    return os.path.join(output_dir, filename)

def format_date_pt(date):
    """Format date in Portuguese: '05 Mai (Dom)'"""
    day = date.day
    month = MONTH_NAMES[date.month]
    weekday = WEEKDAY_NAMES[date.weekday()]
    return f"{day:02d} {month} ({weekday})"

def format_week_range_pt(start_date):
    """Format a week range in Portuguese: '20 Mai a 26 Mai'"""
    end_date = start_date + timedelta(days=6)
    start_day = start_date.day
    start_month = MONTH_NAMES[start_date.month]
    end_day = end_date.day
    end_month = MONTH_NAMES[end_date.month]
    if start_month == end_month:
        return f"{start_day:02d} a {end_day:02d} {end_month}"
    else:
        return f"{start_day:02d} {start_month} a {end_day:02d} {end_month}"

def generate_html_content(final_schedule, task_codes, task_symbols, task_descriptions, 
                         task_short_descriptions, task_css_colors, category_title, 
                         start_date, people_symbols):
    """Generate the HTML content for the schedule"""
    
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset=\"UTF-8\">
    <title>{category_title}</title>
    <style>
        body {
            font-family: 'Helvetica', 'Arial', sans-serif;
            line-height: 1.6;
            color: #222;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            background: #f8f9fa;
        }
        h1 {
            text-align: center;
            color: #2c3e50;
            padding: 6px;
            margin-bottom: 15px;
            border-bottom: 2px solid #ecf0f1;
            font-size: 2em;
        }
        .legend {
            margin: 10px 0;
            border-collapse: collapse;
            width: 100%;
            background: #fff;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 8px #0001;
        }
        .legend th {
            background-color: #ffe066;
            text-align: left;
            padding: 8px 6px;
            font-size: 1em;
        }
        .legend td {
            padding: 6px;
            border: 1px solid #eee;
            font-size: 0.9em;
        }
        .task-emoji {
            font-size: 1.2em;
            margin-right: 5px;
        }
        .task-title {
            font-weight: bold;
            font-size: 1.1em;
        }
"""
    # Generate specific styles for each task's CSS class
    for code in task_codes:
        short_desc = task_short_descriptions[code].lower()
        color = task_css_colors.get(code, '#333333')
        html_content += f"""        .task-{short_desc} {{ 
            color: {color}; 
            font-weight: bold; 
        }}
"""
    
    # Continue with the rest of the CSS
    html_content += """        .schedule {
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
            background: #fff;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 8px #0001;
            table-layout: fixed;
        }
        .schedule th {
            background-color: #1a5fb4;
            color: #fff;
            padding: 14px 8px;
            text-align: center;
            font-size: 1.1em;
            letter-spacing: 1px;
        }
        .schedule .task-header {
            display: inline-block;
            padding: 3px 8px;
            border-radius: 4px;
            background-color: rgba(255, 255, 255, 0.15);
            font-weight: bold;
        }
        .schedule .day-col {
            background-color: #1a5fb4;
            color: #fff;
            font-weight: bold;
            padding: 6px 4px;
            text-align: center;
            width: 120px;
        }
        .schedule td {
            border: 1px solid #eee;
            padding: 8px 4px;
            text-align: center;
            font-size: 0.9em;
            height: 40px;
            vertical-align: middle;
        }
        .schedule tr:nth-child(even) {
            background-color: #f4f8fb;
        }
        .footer {
            text-align: center;
            margin-top: 30px;
            color: #7f8c8d;
            font-size: 1em;
        }
        @media print {
            body {
                padding: 0;
                margin: 0;
                background: #fff;
                font-size: 95%;
            }
            h1 {
                margin-top: 10px;
                margin-bottom: 10px;
                page-break-after: avoid;
            }
            .schedule {
                page-break-inside: auto;
                margin: 10px 0;
            }
            .schedule tr {
                page-break-inside: avoid;
                page-break-after: auto;
            }
            .page-break {
                page-break-after: always;
            }
            .legend {
                page-break-inside: avoid;
            }
            tr {
                break-inside: avoid;
            }
        }
    </style>
</head>
<body>
    <h1>🔀 {category_title.upper()} 🔀</h1>
    <table class=\"legend\">
        <tr>
            <th>Tarefa</th>
            <th>Descrição</th>
        </tr>
"""
    # Include emoji directly with task name
    for i, code in enumerate(task_codes):
        short_desc = task_short_descriptions[code].lower()
        task_class = f"task-{short_desc}"
        html_content += f"""
        <tr>
            <td><span class="{task_class} task-title"><span class="task-emoji">{task_symbols[code]}</span>{task_short_descriptions[code]}</span></td>
            <td>{task_descriptions[code]}</td>
        </tr>"""
    html_content += """
    </table>
    <table class=\"schedule\">
        <tr>
            <th>Semana</th>
"""
    # Use white text with background color in table headers for better contrast
    for code in task_codes:
        short_desc = task_short_descriptions[code]
        html_content += f'            <th><span class="task-header">{task_symbols[code]} {short_desc}</span></th>\n'
    html_content += "        </tr>\n"
    
    # Generate actual calendar dates with Portuguese month names
    for week_num, day in enumerate(final_schedule, 0):
        current_date = start_date + timedelta(weeks=week_num)
        date_str = format_week_range_pt(current_date)
        
        # Add page break after week 10, 20, 30, etc.
        page_break_class = ' class="page-break"' if (week_num + 1) % 10 == 0 else ''
        
        html_content += f"        <tr{page_break_class}>\n            <td class=\"day-col\">{date_str}</td>\n"
        for code in task_codes:
            if code in day:
                p1, p2 = day[code]
                html_content += f'            <td>{p1} {people_symbols[p1]} ⟷ {p2} {people_symbols[p2]}</td>\n'
            else:
                html_content += '            <td></td>\n'
        html_content += "        </tr>\n"
    
    # Close the table properly
    html_content += """    </table>
    
    <div class=\"footer\">
        <p>Feito por Afonso ❤️</p>
        <p><em>Cada linha representa uma semana completa (segunda a domingo).</em></p>
    </div>
</body>
</html>
"""
    return html_content

def export_schedule_to_html(final_schedule, filename=None, start_date=None, category="kitchen"):
    """
    Export the schedule to a beautiful HTML file that's ready to print.
    
    Parameters:
    - final_schedule: The schedule data
    - filename: Output HTML filename
    - start_date: Starting date (default: May 20, 2024)
    - category: Schedule category
    """
    # Import task-related data
    from tarefas_tasks import (create_task_collections, PEOPLE_SYMBOLS, CATEGORIES)
    
    # Set appropriate output path if none provided
    if filename is None:
        filename = f"{category}_rotation.html"
        filename = get_output_path(filename, category)
        
    # Get category-specific task collections for proper rendering
    collections = create_task_collections(category)
    task_codes = collections['TASK_CODES']
    task_symbols = collections['TASK_SYMBOLS']
    task_descriptions = collections['TASK_DESCRIPTIONS']
    task_short_descriptions = collections['TASK_SHORT_DESCRIPTIONS']
    task_css_colors = collections['TASK_CSS_COLORS']
    
    # Set default start date if none provided
    if start_date is None:
        start_date = datetime(2024, 5, 20)  # May 20, 2024
    
    # Get category title
    category_title = CATEGORIES.get(category, "TAREFAS")
    
    # Generate HTML content
    html_content = generate_html_content(
        final_schedule, task_codes, task_symbols, task_descriptions,
        task_short_descriptions, task_css_colors, category_title, 
        start_date, PEOPLE_SYMBOLS
    )
    
    # Write HTML file
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"HTML exported to {filename}")
    print(f"Opening {filename} in browser.")
    webbrowser.open('file://' + os.path.realpath(filename))
    return filename

def export_schedule_to_pdf(final_schedule, filename=None, start_date=None, category="kitchen"):
    """
    For PDF export, we'll first create an HTML file and, if possible, convert it to PDF using WeasyPrint.
    """
    # Default filename based on category
    if filename is None:
        filename = f"{category}_rotation.pdf"
    
    # Get full path for output file
    output_path = get_output_path(filename, category)
    
    # HTML file has same name with .html extension
    html_filename = os.path.basename(filename).replace('.pdf', '.html')
    
    # Export to HTML first
    html_path = export_schedule_to_html(
        final_schedule, 
        filename=get_output_path(html_filename, category), 
        start_date=start_date, 
        category=category
    )
    
    try:
        from weasyprint import HTML
        HTML(html_path).write_pdf(output_path)
        print(f"PDF exported to {output_path}")
    except ImportError:
        print("[WARNING] WeasyPrint not installed! HTML version generated only.")
        print("For perfect PDF, install with: pip install weasyprint && sudo apt install libpango-1.0-0 libpangocairo-1.0-0 libcairo2")
        print("HTML opened in browser. Use Ctrl+P to print or save as PDF.")

def save_schedule_json(final_schedule, filename=None, category="kitchen"):
    """Save the schedule to a JSON file for later reuse"""
    if filename is None:
        filename = f"{category}_rotation.json"
    
    # Get full path for output file
    output_path = get_output_path(filename, category)
    
    # Create a data structure to save both the schedule and metadata
    data = {
        'category': category,
        'schedule': final_schedule
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Schedule saved to {output_path}")

def load_schedule_json(filename=None, category="kitchen"):
    """Load a schedule from a previously saved JSON file"""
    if filename is None:
        filename = f"{category}_rotation.json"
        
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Handle both new and old format
        if isinstance(data, dict) and 'schedule' in data:
            return data['schedule']
        else:
            # Old format without metadata
            return data
    except FileNotFoundError:
        # Check if there's an old-style file in the root directory
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"Using old file {filename} in project root (will migrate to new location)")
            
            # Save it to the new location for future use
            if isinstance(data, dict) and 'schedule' in data:
                save_schedule_json(data['schedule'], category=category)
                return data['schedule']
            else:
                save_schedule_json(data, category=category)
                return data
        except FileNotFoundError:
            print(f"Error: File {filename} not found.")
            exit(1) 