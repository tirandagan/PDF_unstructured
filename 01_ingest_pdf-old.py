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


Usage:
Ensure all dependencies are installed and the config.ini file is properly set up with API keys.
Run the script to process all PDF files in the specified input directory and optionally generate 
annotated visualizations.

-----------------------------------------------------------------
(C) 2024 Prof. Tiran Dagan, FDU University. All rights reserved.
-----------------------------------------------------------------
"""

import os
import logging
from helpers.config import load_configuration, get_config
from helpers.pdf_ingest import ingest_pdfs, create_bbox_images

# Remove or comment out the existing logging setup
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

def get_pdf_files(input_dir):
    return [f for f in os.listdir(input_dir) if f.lower().endswith('.pdf')]

def get_output_json_path(pdf_file):
    output_dir = os.path.realpath(get_config('DIRECTORIES', 'OUTPUT_DIR'))
    return os.path.join(output_dir, f"{pdf_file}.json")

def main():
    if not load_configuration():
        return

    input_dir = os.path.realpath(get_config('DIRECTORIES', 'INPUT_DIR'))
    pdf_files = get_pdf_files(input_dir)
    save_bbox_files = get_config('PDF_PROCESSING', 'SAVE_BBOX_IMAGES')
    
    total_files = len(pdf_files)
    logging.info(f"Total files to process: {total_files}")

    files_to_process = []
    for pdf_file in pdf_files:
        output_json = get_output_json_path(pdf_file)
        if os.path.exists(output_json):
            user_input = input(f"Output JSON already exists for {pdf_file}. Reprocess? (y/n): ").lower()
            if user_input == 'y':
                files_to_process.append(pdf_file)
            else:
                logging.info(f"Skipping {pdf_file}")
        else:
            files_to_process.append(pdf_file)

    if files_to_process:
        ingest_results = ingest_pdfs(input_dir, files_to_process)
        
        if ingest_results:
            logging.info("Document elements saved as JSON files in the output directory.")

        if save_bbox_files:
            logging.info("Creating Bounding box images")
            create_bbox_images(input_dir, files_to_process)
    else:
        logging.info("No files to process.")

if __name__ == "__main__":
    main()
    