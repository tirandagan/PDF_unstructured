import curses
import logging
import os
from curses.textpad import Textbox, rectangle
from helpers import *


def setup_logging():
    # Clear the log file
    with open('pdf_converter.log', 'w') as log_file:
        pass
    
    logging.basicConfig(filename='pdf_converter.log', level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')

def process_pdfs(stdscr, pdf_files):
    input_dir = global_config.get('DIRECTORIES', 'input_dir')
    output_dir = global_config.get('DIRECTORIES', 'output_dir')
    save_bbox_images = global_config.get('PDF_PROCESSING', 'save_bbox_images')
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Ingest PDFs
    ingest_pdfs(input_dir, pdf_files)
    
    # Process each PDF
    for pdf_file in pdf_files:
        try:
            file_path = os.path.join(input_dir, pdf_file)
            num_pages = get_pdf_page_count(file_path)
            
            # Create a simple progress bar
            def progress_bar():
                nonlocal current_page
                current_page += 1
                progress = int((current_page / num_pages) * 50)
                stdscr.addstr(curses.LINES - 3, 2, f"[{'#' * progress}{' ' * (50 - progress)}] {current_page}/{num_pages}")
                stdscr.refresh()
            
            current_page = 0
            progress_bar.text = lambda msg: stdscr.addstr(curses.LINES - 4, 2, msg.ljust(curses.COLS - 4))
            
            # Process the PDF annotations
            if save_bbox_images:
                process_pdf_pages(pdf_file, num_pages, progress_bar)
            
            logging.info(f"Processed {pdf_file}")
        except Exception as e:
            logging.error(f"Error processing {pdf_file}: {str(e)}")
    
    
    # After processing all PDFs, wait for user input
    stdscr.addstr(curses.LINES - 2, 2, "PDF processing complete. Press any key to continue.", curses.color_pair(3))
    stdscr.refresh()
    stdscr.getch()


def main(stdscr):
        
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
        
        key = stdscr.getch()

        if key == curses.KEY_UP:
            selected_index = (selected_index - 1) % len(all_settings)
        elif key == curses.KEY_DOWN:
            selected_index = (selected_index + 1) % len(all_settings)
        elif key == curses.KEY_F2:
            edit_config(stdscr, selected_index)
        elif key == curses.KEY_F10:
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
        elif key == curses.KEY_F9:
            break

        stdscr.clear()
        stdscr.refresh()

if __name__ == "__main__":
    setup_logging()
    curses.wrapper(main)
