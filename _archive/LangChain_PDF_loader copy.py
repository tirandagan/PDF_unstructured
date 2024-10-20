"""
LangChain PDF Loader and Analyzer

This script demonstrates the use of LangChain's UnstructuredLoader to process and analyze PDF documents.
It extracts text and metadata from all PDF files in a specified directory, focusing on document structure 
and content categorization.

Copyright © 2024 Prof. Tiran Dagan, FDU University. All rights reserved.

Main functionalities:
1. Load and parse multiple PDF documents using UnstructuredLoader
2. Extract text and metadata from the PDFs
3. Analyze and categorize document elements (e.g., text, titles, images, tables)
4. Optionally visualize the document structure using custom helper functions
5. Display progress across files and pages using alive_progress

Dependencies:
- langchain_unstructured
- configparser
- matplotlib
- pillow
- custom 'helpers' module
- alive_progress

Usage:
Ensure all dependencies are installed and the config.ini file is properly set up with API keys.
Run the script to process all PDF files in the specified input directory and optionally generate 
annotated visualizations.

Source: https://python.langchain.com/docs/how_to/document_loader_pdf/
"""

import logging
from alive_progress import alive_bar, config_handler
from helpers.config import load_configuration, get_config
from helpers.pdf_box_plotting import get_pdf_page_count
from helpers.pdf_processing import process_pdf_pages

# Configure alive_progress
config_handler.set_global(length=50, spinner="dots", bar="smooth", enrich_print=True)

def pre_process_pdfs(input_dir):
    """Prepare PDF files for processing by counting pages and gathering file info."""
    import os
    pdf_files = [f for f in os.listdir(input_dir) if f.lower().endswith('.pdf')]
    total_files = len(pdf_files)
    logging.info(f"Found {total_files} PDF files in {input_dir}")

    pdf_info = []
    total_pages = 0
    for input_file in pdf_files:
        file_path = os.path.join(input_dir, input_file)
        num_pages = get_pdf_page_count(file_path)
        total_pages += num_pages
        pdf_info.append((file_path, num_pages))

    return pdf_info, total_pages

def main():
    config = load_configuration()
    if not config:
        return
'''
    input_dir = get_config('DIRECTORIES', 'INPUT_DIR')
    output_dir = get_config('DIRECTORIES', 'OUTPUT_DIR')
    save_images = get_config('PDF_PROCESSING', 'SAVE_IMAGES').lower() == 'true'
    save_document_elements = get_config('PDF_PROCESSING', 'SAVE_DOCUMENT_ELEMENTS').lower() == 'true'
'''

    pdf_info, total_pages = pre_process_pdfs(input_dir)
    logging.info(f"Total pages to process: {total_pages}")

    with alive_bar(total_pages, title="Processing PDFs", enrich_print=False) as bar:
        process_pdf_pages(pdf_info, save_images, output_dir, bar)

    if save_document_elements:
        logging.info("Document elements saved as JSON files in the output directory.")

    logging.info("Finished processing all PDF files")

if __name__ == "__main__":
    main()
