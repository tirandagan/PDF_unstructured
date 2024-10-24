"""
-----------------------------------------------------------------
(C) 2024 Prof. Tiran Dagan, FDU University. All rights reserved.
-----------------------------------------------------------------

Display and User Interaction Utilities

This module provides functions for displaying configuration settings
and handling user interactions in a terminal-based interface using curses.

Key features:
- Display and edit configuration settings
- Validate directory paths
- Handle user input for navigation and selection

Usage:
- Use `draw_windows()` to render the main interface.
- Use `edit_config()` to allow users to edit configuration settings.
"""

import curses
import os
from .field_settings import FIELD_CONFIG
from .config import save_config, global_config
import logging
import json


WINDOW_DIMENSIONS = {
    "Configuration": {"width_percent": 33, "height_percent": 60},
    "PDF Files": {"width_percent": 33, "height_percent": 60},
    "File Progress": {"width_percent": 33, "height_percent": 60},
    "Log": {"width_percent": 100, "height_percent": 40}
}

def get_friendly_name(key):
    """
    Retrieve the friendly name for a configuration key.

    Args:
        key (str): The configuration key.

    Returns:
        str: The friendly name.
    """
    return FIELD_CONFIG[key]['friendly_name']

def get_dropdown_options(key):
    """
    Retrieve dropdown options for a list-type configuration key.

    Args:
        key (str): The configuration key.

    Returns:
        list: The list of options.
    """
    field_config = FIELD_CONFIG.get(key.upper(), {})
    return field_config.get('options', []) if field_config.get('type') == 'list' else []

def is_boolean_field(key):
    """
    Check if a configuration key is of boolean type.

    Args:
        key (str): The configuration key.

    Returns:
        bool: True if the key is boolean, False otherwise.
    """
    return FIELD_CONFIG.get(key.upper(), {}).get('type') == 'boolean'

def is_valid_directory(path):
    """
    Validate if a path is a directory.

    Args:
        path (str): The path to validate.

    Returns:
        bool: True if the path is a directory, False otherwise.
    """
    return os.path.isdir(path)

def edit_config(stdscr, selected_index):
    """
    Edit a configuration setting based on user input.

    Args:
        stdscr: The curses screen object.
        selected_index (int): The index of the selected configuration setting.
    """
    all_settings = []
    for key, field_config in FIELD_CONFIG.items():
        section = field_config['section']
        all_settings.append((section, key))
    
    section, key = all_settings[selected_index]
    field_config = FIELD_CONFIG[key]
    friendly_name = field_config['friendly_name']
    current_value = global_config.get(section, key)
    
    height, width = stdscr.getmaxyx()
    curses.curs_set(1)

    # Determine edit window width and height
    edit_width = min(field_config.get('max_length', 30), width - 4)
    
    if field_config['type'] == 'list':
        options = field_config['options']
        edit_height = len(options) + 4  # Add space for title, instructions, and borders
    elif field_config['type'] == 'boolean':
        edit_height = 6  # 2 for options, 1 for title, 1 for instructions, 2 for borders
    else:
        edit_height = 5  # 1 for title, 1 for edit field, 1 for instructions, 2 for borders

    # Calculate position for centered window
    start_y = (height - edit_height) // 2
    start_x = (width - edit_width) // 2

    # Create edit window
    editwin = curses.newwin(edit_height, edit_width, start_y, start_x)
    editwin.keypad(1)  # Enable keypad mode
    editwin.box()
    editwin.addstr(0, 2, friendly_name, curses.A_REVERSE)
    
    if field_config['type'] == 'list':
        instruction = "Use arrow keys, Enter to confirm, ESC to cancel"
    elif field_config['type'] == 'boolean':
        instruction = "Use arrow keys, Enter to confirm, ESC to cancel"
    else:
        instruction = "Enter to confirm, ESC to cancel"
    
    editwin.addstr(edit_height - 1, 2, instruction[:edit_width - 4])
    editwin.refresh()

    if field_config['type'] == 'list':
        options = field_config['options']
        current_index = options.index(current_value) if current_value in options else 0
        while True:
            for i, option in enumerate(options):
                if i == current_index:
                    editwin.addstr(i+1, 2, f"> {option:<{edit_width-4}}"[:edit_width-3], curses.A_REVERSE)
                else:
                    editwin.addstr(i+1, 2, f"  {option:<{edit_width-4}}"[:edit_width-3])
            editwin.refresh()
            
            ch = editwin.getch()
            if ch == 27:  # ESC key
                new_value = None
                break
            elif ch == curses.KEY_UP:
                current_index = (current_index - 1) % len(options)
            elif ch == curses.KEY_DOWN:
                current_index = (current_index + 1) % len(options)
            elif ch == 10:  # Enter key
                new_value = options[current_index]
                break
    elif field_config['type'] == 'boolean':
        options = ['True', 'False']
        current_index = 0 if current_value.lower() == 'true' else 1
        while True:
            for i, option in enumerate(options):
                if i == current_index:
                    editwin.addstr(i+1, 2, f"> {option:<{edit_width-4}}"[:edit_width-3], curses.A_REVERSE)
                else:
                    editwin.addstr(i+1, 2, f"  {option:<{edit_width-4}}"[:edit_width-3])
            editwin.refresh()
            
            ch = editwin.getch()
            if ch == 27:  # ESC key
                new_value = None
                break
            elif ch == curses.KEY_UP or ch == curses.KEY_DOWN:
                current_index = 1 - current_index
            elif ch == 10:  # Enter key
                new_value = options[current_index]
                break
    else:  # Text field
        new_value = current_value
        cursor_x = len(new_value)
        scroll_offset = 0
        max_visible_width = edit_width - 6

        def update_display():
            nonlocal scroll_offset
            if len(new_value) > max_visible_width:
                if cursor_x < scroll_offset:
                    scroll_offset = cursor_x
                elif cursor_x >= scroll_offset + max_visible_width:
                    scroll_offset = cursor_x - max_visible_width + 1
                visible_value = new_value[scroll_offset:scroll_offset + max_visible_width]
                if scroll_offset > 0:
                    visible_value = '<' + visible_value[1:]
                if scroll_offset + max_visible_width < len(new_value):
                    visible_value = visible_value[:-1] + '>'
            else:
                visible_value = new_value
            editwin.addstr(2, 2, visible_value.ljust(max_visible_width))
            editwin.refresh()

        update_display()
        editwin.keypad(1)  # Enable keypad mode to capture special keys
        
        while True:
            editwin.move(2, cursor_x - scroll_offset + 2)
            ch = editwin.getch()
            
            if ch == 27:  # ESC key
                new_value = None
                break
            elif ch == 10:  # Enter key
                break
            elif ch in (curses.KEY_BACKSPACE, 127):  # Backspace
                if cursor_x > 0:
                    new_value = new_value[:cursor_x-1] + new_value[cursor_x:]
                    cursor_x -= 1
            elif ch == curses.KEY_DC:  # Delete key
                if cursor_x < len(new_value):
                    new_value = new_value[:cursor_x] + new_value[cursor_x+1:]
            elif ch == curses.KEY_LEFT:
                if cursor_x > 0:
                    cursor_x -= 1
            elif ch == curses.KEY_RIGHT:
                if cursor_x < len(new_value):
                    cursor_x += 1
            elif ch == curses.KEY_HOME:
                cursor_x = 0
            elif ch == curses.KEY_END:
                cursor_x = len(new_value)
            elif 32 <= ch <= 126:  # Printable characters
                new_value = new_value[:cursor_x] + chr(ch) + new_value[cursor_x:]
                cursor_x += 1
            
            update_display()

        curses.curs_set(0)  # Hide cursor

    if new_value is not None and new_value != current_value:
        global_config.set(section, key, new_value)
        save_config()

    curses.curs_set(0)
    
def display_config(win, selected_index, color_pair):
    """
    Display the current configuration settings in a window.

    Args:
        win: The curses window object.
        selected_index (int): The index of the selected configuration setting.
        color_pair: The color pair to use for displaying text.
    """
    logging.debug(f"display_config using global_config: {global_config}")
    
    win.clear()
    win.box()
    win.addstr(0, 2, "Configuration", curses.A_REVERSE)
    
    all_settings = []
    for key, field_config in FIELD_CONFIG.items():
        section = field_config['section']
        all_settings.append((section, key))
    
    max_display = win.getmaxyx()[0] - 2
    start_index = max(0, selected_index - max_display + 1)
    end_index = min(len(all_settings), start_index + max_display)
    
    for i, (section, key) in enumerate(all_settings[start_index:end_index], start=1):
        friendly_name = get_friendly_name(key)
        value = global_config.get(section, key)
        if FIELD_CONFIG[key]['type'] == 'string' and key.lower().endswith(('password', 'key', 'secret')):
            value = '*' * 10
        
        # Check if the setting is a directory and if it's invalid
        is_invalid_dir = (key in ['INPUT_DIR', 'OUTPUT_DIR']) and not is_valid_directory(value)
        
        if i + start_index - 1 == selected_index:
            attr = curses.A_REVERSE
        else:
            attr = curses.A_NORMAL
        
        if is_invalid_dir:
            win.attron(curses.color_pair(5))  # Red text for invalid directories
        
        win.addstr(i, 2, f"{'>' if i + start_index - 1 == selected_index else ' '} {friendly_name}: {value}", attr | curses.color_pair(color_pair))
        
        if is_invalid_dir:
            win.attroff(curses.color_pair(5))
    
    win.refresh()
    
def draw_windows(stdscr, selected_index, current_pdf=None, current_page=None, total_pages=None):
    """
    Draw the main interface windows for configuration, PDF list, progress, and logs.

    Args:
        stdscr: The curses screen object.
        selected_index (int): The index of the selected configuration setting.
        current_pdf (str): The current PDF being processed.
        current_page (int): The current page number being processed.
        total_pages (int): The total number of pages in the current PDF.
    """
    logging.debug(f"draw_windows using global_config: {global_config}")

    # Color initialization with updated colors
    curses.start_color()
    curses.init_pair(1, curses.COLOR_MAGENTA, curses.COLOR_BLACK)  # Magenta on black for main windows
    curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK)     # Cyan on black for PDF list
    curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)    # Green on black for progress
    curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK)   # Yellow on black for highlighting
    curses.init_pair(5, curses.COLOR_RED, curses.COLOR_BLACK)      # Red on black for error messages
    curses.init_pair(6, curses.COLOR_WHITE, curses.COLOR_BLACK)    # Light grey (white) on black for Configuration text

    # Configuration Window
    top, left, bottom, right = get_window_info("Configuration", stdscr)
    config_win = curses.newwin(bottom - top, right - left, top, left)
    config_win.bkgd(' ', curses.color_pair(1))
    config_win.box()
    config_win.addstr(0, 2, "Configuration", curses.A_REVERSE)
    display_config(config_win, selected_index, color_pair=6)  # Pass the color pair for text

    # PDF Files Window - Split into Input and Output
    top, left, bottom, right = get_window_info("PDF Files", stdscr)
    mid_point = (bottom - top) // 2

    # Input Files Window
    input_win = curses.newwin(mid_point, right - left, top, left)
    input_win.bkgd(' ', curses.color_pair(2))
    input_win.box()
    input_win.addstr(0, 2, "Input Files", curses.A_REVERSE)
    input_dir = global_config.get('DIRECTORIES', 'input_dir')
    if is_valid_directory(input_dir):
        pdf_files = [f for f in os.listdir(input_dir) if f.endswith('.pdf')]
        for i, pdf in enumerate(pdf_files):
            if i < mid_point - 2:
                if pdf == current_pdf:
                    input_win.addstr(i + 1, 2, pdf[:right - left - 4], curses.color_pair(4) | curses.A_BOLD)
                else:
                    input_win.addstr(i + 1, 2, pdf[:right - left - 4])
    else:
        input_win.addstr(1, 2, "Invalid Input Folder", curses.color_pair(5))
    input_win.refresh()

    # Output Files Window
    output_win = curses.newwin(bottom - top - mid_point, right - left, top + mid_point, left)
    output_win.bkgd(' ', curses.color_pair(2))
    output_win.box()
    output_win.addstr(0, 2, "Output Files", curses.A_REVERSE)
    output_dir = global_config.get('DIRECTORIES', 'output_dir')
    if is_valid_directory(output_dir):
        output_files = [f for f in os.listdir(output_dir) if f.endswith('.json') or f.endswith('.jpg')]
        output_files.sort()  # Sort files for better organization
        line = 1
        json_files = [f for f in output_files if f.endswith('.json')]
        jpg_files = [f for f in output_files if f.endswith('.jpg')]

        for json_file in json_files:
            if line >= bottom - top - mid_point - 1:
                break  # Handle overflow
            base_name = os.path.splitext(json_file)[0]

            # Determine LLM enhancement status
            json_path = os.path.join(output_dir, json_file)
            with open(json_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
                total_images = sum(1 for item in json_data if item['type'] == 'Image')
                llm_summaries = sum(1 for item in json_data if item['type'] == 'Image' and 'llm_summary' in item)
                if llm_summaries == total_images:
                    llm_status = "{LLM enhanced}"
                elif llm_summaries > 0:
                    llm_status = "{LLM partial}"
                else:
                    llm_status = ""

            output_win.addstr(line, 2, f"{base_name} {{JSON}} {llm_status}", curses.color_pair(4))
            line += 1

            # List corresponding JPG files
            name_only=base_name.split('.')[0]
            related_jpgs = [jpg for jpg in jpg_files if jpg.startswith(name_only)]
            for jpg in related_jpgs:
                if line >= bottom - top - mid_point - 1:
                    break  # Handle overflow
                page_info = jpg.split('-')[-2]  # Extract page number from filename
                output_win.addstr(line, 4, f"pg {page_info} annotation {{JPG}}", curses.color_pair(4))
                line += 1
    else:
        output_win.addstr(1, 2, "Invalid Output Folder", curses.color_pair(5))
    output_win.refresh()

    # File Progress Window
    top, left, bottom, right = get_window_info("File Progress", stdscr)
    progress_win = curses.newwin(bottom - top, right - left, top, left)
    progress_win.bkgd(' ', curses.color_pair(3))
    progress_win.box()
    progress_win.addstr(0, 2, "File Progress", curses.A_REVERSE)
    if current_pdf and current_page and total_pages:
        progress_win.addstr(1, 2, f"Processing: {current_pdf}"[:right - left - 4])
        progress_win.addstr(2, 2, f"Page {current_page} of {total_pages}"[:right - left - 4])
        progress_percentage = (current_page / total_pages) * 100
        progress_bar = f"[{'#' * int(progress_percentage / 2):{50}}]"
        progress_win.addstr(3, 2, progress_bar[:right - left - 4])
        progress_win.addstr(4, 2, f"{progress_percentage:.1f}% complete"[:right - left - 4])
    progress_win.refresh()

    # Log Window
    top, left, bottom, right = get_window_info("Log", stdscr)
    log_win_height = bottom - top
    log_win_width = right - left

    if log_win_height > 2 and log_win_width > 4:
        log_win = curses.newwin(log_win_height, log_win_width, top, left)
        log_win.bkgd(' ', curses.color_pair(1))
        log_win.box()
        log_win.addstr(0, 2, "Log", curses.A_REVERSE)
        try:
            with open('pdf_converter.log', 'r') as log_file:
                logs = log_file.readlines()[-(log_win_height - 2):]
                if logs:
                    for i, log in enumerate(logs):
                        max_log_width = log_win_width - 4
                        if max_log_width > 0:
                            log_win.addstr(i + 1, 2, log.strip()[:max_log_width])
                else:
                    log_win.addstr(1, 2, "No logs yet.")
        except FileNotFoundError:
            log_win.addstr(1, 2, "No logs yet.")
        log_win.refresh()
    else:
        stdscr.addstr(curses.LINES - 2, 0, "Terminal too small for log window.", curses.color_pair(5))

    # Status Bar
    status_bar_text = "F2: Edit Configuration | ^O: Run Task | F9: Exit"
    stdscr.addstr(curses.LINES - 1, 0, status_bar_text[:curses.COLS - 1], curses.A_REVERSE)
    stdscr.refresh()

def get_window_info(window_name, stdscr):
    """
    Returns the writable coordinates for a given window name.

    Args:
        window_name (str): The name of the window.
        stdscr: The curses screen object.

    Returns:
        tuple: A tuple containing the top-left and bottom-right coordinates
               (top, left, bottom, right) for the writable area.
    """
    height, width = stdscr.getmaxyx()
    window = WINDOW_DIMENSIONS.get(window_name, {})
    width_percent = window.get("width_percent", 0)
    height_percent = window.get("height_percent", 0)

    win_width = width * width_percent // 100
    win_height = height * height_percent // 100

    if window_name == "Configuration":
        top, left = 0, 0
    elif window_name == "PDF Files":
        top, left = 0, win_width
    elif window_name == "File Progress":
        top, left = 0, 2 * win_width
    elif window_name == "Log":
        # Calculate the top position based on the height of the top windows
        top = height * 60 // 100  # Assuming top windows take 60% of the height
        left = 0
    else:
        return (0, 0, 0, 0)

    bottom = min(top + win_height, height - 1)  # Ensure it doesn't exceed screen height
    right = min(left + win_width, width - 1)    # Ensure it doesn't exceed screen width

    return (top, left, bottom, right)

def update_log_window(stdscr):
    """
    Updates the log window with the latest content from the log file.

    Args:
        stdscr: The curses screen object.
    """
    top, left, bottom, right = get_window_info("Log", stdscr)
    log_win_height = bottom - top
    log_win_width = right - left

    if log_win_height > 2 and log_win_width > 4:
        log_win = curses.newwin(log_win_height, log_win_width, top, left)
        log_win.bkgd(' ', curses.color_pair(1))
        log_win.box()
        log_win.addstr(0, 2, "Log", curses.A_REVERSE)
        try:
            with open('pdf_converter.log', 'r') as log_file:
                logs = log_file.readlines()[-(log_win_height - 2):]  # Scroll to the bottom
                if logs:
                    for i, log in enumerate(logs):
                        max_log_width = log_win_width - 4
                        if max_log_width > 0:
                            log_win.addstr(i + 1, 2, log.strip()[:max_log_width])
                else:
                    log_win.addstr(1, 2, "No logs yet.")
        except FileNotFoundError:
            log_win.addstr(1, 2, "No logs yet.")
        log_win.refresh()
    else:
        stdscr.addstr(curses.LINES - 2, 0, "Terminal too small for log window.", curses.color_pair(5))






