#!/usr/bin/env python3
"""
Task Rotation Scheduler - Run All Categories
This script runs the scheduler for all categories and exports PDFs
"""

import os
import sys
import subprocess
import argparse
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

def run_command(cmd, description=None):
    """Run a command with colorful output"""
    if description:
        print(f"{Fore.CYAN}{Style.BRIGHT}🚀 {description}...{Style.RESET_ALL}")
    
    print(f"{Fore.YELLOW}$ {' '.join(cmd)}{Style.RESET_ALL}")
    result = subprocess.run(cmd, capture_output=False)
    
    if result.returncode == 0:
        print(f"{Fore.GREEN}✓ Success!{Style.RESET_ALL}\n")
        return True
    else:
        print(f"{Fore.RED}✗ Failed (code {result.returncode}){Style.RESET_ALL}\n")
        return False

def main():
    parser_args = [sys.executable, "tarefas.py"]
    categories = ["kitchen", "clothing", "cats"]
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run all task categories")
    parser.add_argument("--solver-only", action="store_true", help="Only run the solver, don't generate PDFs")
    parser.add_argument("--pdf-only", action="store_true", help="Only generate PDFs from existing JSON files")
    parser.add_argument("--start-date", type=str, help="Starting date in DD/MM/YYYY format (defaults to next Monday)")
    args = parser.parse_args()
    
    # Default command arguments
    cmd_args = ["-a"]  # Auto-days by default
    if args.start_date:
        cmd_args.extend(["--start-date", args.start_date])
    
    if args.pdf_only:
        print(f"{Fore.MAGENTA}{Style.BRIGHT}🖨️  PDF-ONLY MODE: Using saved JSON files{Style.RESET_ALL}")
        cmd_args = ["--from-json", "--pdf"]
    elif not args.solver_only:
        # Add PDF flag unless we're in solver-only mode
        cmd_args.append("--pdf")
    
    print(f"\n{Fore.MAGENTA}{'='*50}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}{Style.BRIGHT}🔄 RUNNING ALL TASK CATEGORIES 🔄{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}{'='*50}{Style.RESET_ALL}\n")
    
    for category in categories:
        # Build category-specific command
        category_cmd = parser_args + ["-c", category] + cmd_args
        desc = f"Processing {category.upper()} category"
        success = run_command(category_cmd, desc)
        
        if not success and not args.pdf_only:
            print(f"{Fore.YELLOW}Skipping PDF generation for {category} due to solver failure{Style.RESET_ALL}")
    
    print(f"\n{Fore.GREEN}{Style.BRIGHT}🎉 ALL DONE! 🎉{Style.RESET_ALL}")
    print(f"Output files are in the {Fore.CYAN}output/{Style.RESET_ALL} directory.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}Interrupted. Exiting.{Style.RESET_ALL}")
        sys.exit(1) 