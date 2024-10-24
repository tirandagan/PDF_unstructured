"""
-----------------------------------------------------------------
(C) 2024 Prof. Tiran Dagan, FDU University. All rights reserved.
-----------------------------------------------------------------

PDF Ingestion and Processing Application

This script provides a terminal-based interface for processing PDF files.
It allows users to configure settings, select PDF files from an input directory,
and process them to extract annotations and optionally save bounding box images.

Key features:
- Terminal-based user interface using curses
- Configurable input and output directories
- Progress bar for PDF processing
- Error handling and logging

Usage:
python 01_RAG_ingest_app.py

Controls:
- Arrow keys: Navigate settings
- F2: Edit configuration
- F10: Start PDF processing
- F9: Exit the application
"""

import curses
import logging
import os
import json
from curses.textpad import Textbox, rectangle
from helpers import *
from tqdm import tqdm


def setup_logging():
    """
    Sets up logging for the application. Clears the existing log file and
    configures logging to write to 'pdf_converter.log'.
    """
    # Clear the log file
    with open('pdf_converter.log', 'w') as log_file:
        pass
    
    logging.basicConfig(filename='pdf_converter.log', level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')

def process_pdfs(stdscr, pdf_files):
    """
    Processes a list of PDF files, extracting annotations and optionally saving
    bounding box images. Displays a progress bar for each PDF.

    Args:
        stdscr: The curses screen object.
        pdf_files: List of PDF filenames to process.
    """
    input_dir = global_config.get('DIRECTORIES', 'input_dir')
    output_dir = global_config.get('DIRECTORIES', 'output_dir')
    save_bbox_images = global_config.get('PDF_PROCESSING', 'save_bbox_images')
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Ingest PDFs
    ingest_pdfs(input_dir, pdf_files)
    
    # Get writable coordinates for the "File Progress" window
    top, left, bottom, right = get_window_info("File Progress", stdscr)
    progress_win_height = bottom - top
    progress_win_width = right - left
    
    # Process each PDF
    for pdf_file in pdf_files:
        try:
            file_path = os.path.join(input_dir, pdf_file)
            num_pages = get_pdf_page_count(file_path)
            
            # Create a simple progress bar
            def progress_bar():
                nonlocal current_page
                current_page += 1
                progress = int((current_page / num_pages) * (progress_win_width - 12))  # Adjust width for progress bar
                progress_win = curses.newwin(progress_win_height, progress_win_width, top, left)
                progress_win.bkgd(' ', curses.color_pair(3))
                progress_win.box()
                progress_win.addstr(0, 2, "File Progress", curses.A_REVERSE)
                progress_win.addstr(1, 2, f"Analyzing {pdf_file}"[:progress_win_width - 4])
                progress_bar_str = f"[{'#' * progress}{' ' * ((progress_win_width - 12) - progress)}]"
                page_info = f"{current_page}/{num_pages}"
                progress_win.addstr(2, 2, progress_bar_str)
                progress_win.addstr(2, progress_win_width - len(page_info) - 2, page_info, curses.color_pair(3))
                progress_win.refresh()
            
            current_page = 0
            progress_bar.text = lambda msg: stdscr.addstr(top + 3, left + 2, msg.ljust(progress_win_width - 4), curses.color_pair(3))
            
            # Process the PDF annotations
            if save_bbox_images:
                process_pdf_pages(stdscr, pdf_file, num_pages, progress_bar)
            
            logging.info(f"Processed {pdf_file}")
        except Exception as e:
            logging.error(f"Error processing {pdf_file}: {str(e)}")
    
    # Display completion message in a centered window
    message = "PDF processing complete. Press any key to continue."
    message_height = 5
    message_width = len(message) + 4
    start_y = (curses.LINES - message_height) // 2
    start_x = (curses.COLS - message_width) // 2
    message_win = curses.newwin(message_height, message_width, start_y, start_x)
    message_win.box()
    message_win.addstr(2, 2, message)
    message_win.refresh()
    stdscr.getch()

    # Redraw the main interface windows after processing
    draw_windows(stdscr, 0)

def enhance_images(stdscr):
    """
    Enhances images by summarizing them using the image summarizer script.
    """
    output_dir = os.path.realpath(global_config.get('DIRECTORIES', 'output_dir'))
    json_files = select_json_file(stdscr, output_dir)
    
    if not json_files:
        return
    
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
                enrich_json_with_summaries(stdscr, json_file, json_data)
                update_log_window(stdscr)
            logging.info(f"Enhanced images in {json_file}")
        except Exception as e:
            base_filename = os.path.splitext(os.path.basename(json_file))[0]
            logging.error(f"Error enhancing images in {base_filename}: {str(e)}")
    

def create_markdowns(stdscr):
    """
    Creates markdown files from JSON data using the markdown converter script.
    """
    output_dir = os.path.realpath(global_config['DIRECTORIES']['OUTPUT_DIR'])
    json_file = select_json_file(output_dir)
    
    if not json_file:
        return
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        
        markdown_content = json_to_markdown(json_data)
        markdown_file = os.path.splitext(json_file)[0] + '.md'
        with open(markdown_file, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        logging.info(f"Markdown file created: {markdown_file}")
    except Exception as e:
        logging.error(f"Error creating markdown: {str(e)}")
    
    update_log_window(stdscr)

def select_json_file(stdscr, directory):
    """
    Opens a window to select a JSON file from the specified directory.

    Args:
        stdscr: The curses screen object.
        directory (str): The directory to search for JSON files.

    Returns:
        list: A list of selected JSON file paths, or an empty list if canceled.
    """
    json_files = [f for f in os.listdir(directory) if f.endswith('.json')]
    
    if not json_files:
        stdscr.addstr(curses.LINES - 2, 2, "No JSON files found in the output directory!", curses.color_pair(5))
        stdscr.refresh()
        stdscr.getch()
        return []

    file_win_height = len(json_files) + 5  # Add extra lines for instructions
    file_win_width = max(len(f) for f in json_files) + 4
    start_y = (curses.LINES - file_win_height) // 2
    start_x = (curses.COLS - file_win_width) // 2
    file_win = curses.newwin(file_win_height, file_win_width, start_y, start_x)
    file_win.keypad(True)  # Enable keypad mode to capture special keys
    file_win.box()
    file_win.addstr(0, 2, "Select JSON File", curses.A_REVERSE)
    file_win.addstr(file_win_height - 2, 2, "ESC to cancel, * to select all", curses.A_DIM)

    current_selection = 0
    while True:
        for i, json_file in enumerate(json_files):
            if i == current_selection:
                file_win.addstr(i + 2, 2, json_file, curses.A_REVERSE)
            else:
                file_win.addstr(i + 2, 2, json_file)
        file_win.refresh()

        key = file_win.getch()
        if key == curses.KEY_UP:
            current_selection = (current_selection - 1) % len(json_files)
        elif key == curses.KEY_DOWN:
            current_selection = (current_selection + 1) % len(json_files)
        elif key == 10:  # Enter key
            # Clear the file window and refresh the main screen
            file_win.clear()
            stdscr.refresh()
            return [os.path.join(directory, json_files[current_selection])]
        elif key == 27:  # ESC key
            # Clear the file window and refresh the main screen
            file_win.clear()
            stdscr.refresh()
            return []
        elif key == ord('*'):  # '*' key to select all
            # Clear the file window and refresh the main screen
            file_win.clear()
            stdscr.refresh()
            return [os.path.join(directory, f) for f in json_files]

def main(stdscr):
    """
    Main function to run the PDF processing application. Initializes the curses
    interface, loads configuration, and handles user input for navigating and
    processing PDFs.
    """
    curses.curs_set(0)
    stdscr.clear()
    stdscr.refresh()

    load_config()
    logging.debug(f"Global config in main after load_config: {global_config}")

    # Now you can access global_config properties
    output_dir = global_config.get('DIRECTORIES','output_dir')
    input_dir = global_config.get('DIRECTORIES','input_dir')
    
    selected_index = 0

    all_settings = []
    for key, field_config in FIELD_CONFIG.items():
        section = field_config['section']
        all_settings.append((section, key))

    while True:
        draw_windows(stdscr, selected_index)
        
        # Display the menu bar
        stdscr.addstr(curses.LINES - 1, 0, "F2: Edit Configuration | ^O: Run Task | F9: Exit", curses.A_REVERSE)
        stdscr.refresh()

        key = stdscr.getch()

        if key == curses.KEY_UP:
            selected_index = (selected_index - 1) % len(all_settings)
        elif key == curses.KEY_DOWN:
            selected_index = (selected_index + 1) % len(all_settings)
        elif key == curses.KEY_F2:
            edit_config(stdscr, selected_index)
        elif key == 15:  # Ctrl+O
            task = select_task(stdscr)
            if task == "Ingest PDFs and create JSON & Annotations":
                if is_valid_directory(input_dir) and is_valid_directory(output_dir):
                    pdf_files = [f for f in os.listdir(input_dir) if f.endswith('.pdf')]
                    if pdf_files:
                        process_pdfs(stdscr, pdf_files)
                    else:
                        stdscr.addstr(curses.LINES - 2, 2, "No PDF files found in the input directory!", curses.color_pair(5))
                        stdscr.refresh()
                        stdscr.getch()
                else:
                    stdscr.addstr(curses.LINES - 2, 2, "Error: Invalid input or output directory!", curses.color_pair(5))
                    stdscr.refresh()
                    stdscr.getch()
            elif task == "Enhance Images in JSON with LLM Summaries":
                enhance_images(stdscr)
            elif task == "Create Markdowns from JSON output files  ":
                create_markdowns(stdscr)
        elif key == curses.KEY_F9:
            break

        stdscr.clear()
        stdscr.refresh()

def select_task(stdscr):
    """
    Displays a popup menu to select a task to run.

    Args:
        stdscr: The curses screen object.

    Returns:
        str: The selected task, or None if canceled.
    """
    tasks = [
        "Ingest PDFs and create JSON & Annotations",
        "Enhance Images in JSON with LLM Summaries",
        "Create Markdowns from JSON output files  "
    ]
    task_win_height = len(tasks) + 5  # Add extra line for instructions
    task_win_width = max(len(task) for task in tasks) + 4
    start_y = (curses.LINES - task_win_height) // 2
    start_x = (curses.COLS - task_win_width) // 2
    task_win = curses.newwin(task_win_height, task_win_width, start_y, start_x)
    task_win.keypad(True)  # Enable keypad mode to capture special keys
    task_win.box()
    task_win.addstr(0, 2, "Select Task", curses.A_REVERSE)
    task_win.addstr(task_win_height - 2, 2, "ESC to cancel", curses.A_DIM)

    current_selection = 0
    while True:
        for i, task in enumerate(tasks):
            if i == current_selection:
                task_win.addstr(i + 2, 2, task, curses.A_REVERSE)
            else:
                task_win.addstr(i + 2, 2, task)
        task_win.refresh()

        key = task_win.getch()
        if key == curses.KEY_UP:
            current_selection = (current_selection - 1) % len(tasks)
        elif key == curses.KEY_DOWN:
            current_selection = (current_selection + 1) % len(tasks)
        elif key == 10:  # Enter key
            # Clear the task window and refresh the main screen
            task_win.clear()
            #stdscr.clear()
            stdscr.refresh()
            draw_windows(stdscr, 0)

            return tasks[current_selection]
        elif key == 27:  # ESC key
            # Clear the task window and refresh the main screen
            task_win.clear()
            stdscr.refresh()
            return None

if __name__ == "__main__":
    setup_logging()
    curses.wrapper(main)

