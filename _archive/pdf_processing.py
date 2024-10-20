"""
PDF Processing and Visualization Tool

This module provides functionality to process and visualize PDF pages,
including annotating with bounding boxes for different content types.

Copyright © 2024 Prof. Tiran Dagan, FDU University. All rights reserved.
"""

import fitz
import os
import logging
import json
from helpers.pdf_pre_processing import load_pdf_with_unstructured
from helpers.pdf_box_plotting import plot_pdf_with_boxes
from helpers.config import get_config

def process_pdf_pages(pdf_info, save_images, output_dir, progress_bar):
    """Process all pages of all PDFs with progress tracking."""
    save_document_elements = get_config('PDF_PROCESSING', 'SAVE_DOCUMENT_ELEMENTS').lower() == 'true'
    
    for file_path, num_pages in pdf_info:
        file_name = os.path.basename(file_path)
        progress_bar.text(f"Pre-Processing: {file_name}")
        docs = load_pdf_with_unstructured(file_path)
        
        logging.info(f"Number of documents in {file_name}: {len(docs)}")
        logging.info(f"Number of pages in {file_name}: {num_pages}")

        if save_document_elements:
            save_document_elements_as_json(docs, file_name, output_dir)

        progress_bar.text(f"Analyzing Pages: {file_name}")
        for page_number in range(1, num_pages + 1):
            progress_bar.text(f"Analyzing {file_name}: page {page_number}/{num_pages}")
            process_page(file_path, docs, page_number, save_image=save_images, output_dir=output_dir)
            progress_bar()

def process_page(file_path, docs, page_number, save_image=False, output_dir=None):
    """Process a specific page of a PDF file, analyze it, and optionally save an annotated image."""
    pdf = fitz.open(file_path)
    pdf_page = pdf.load_page(page_number - 1)
    
    page_docs = [doc for doc in docs if doc.metadata.get('page_number') == page_number]
    
    for doc in page_docs:
        category = doc.metadata.get('category', 'Unknown')
        content_preview = doc.page_content[:50] + "..." if len(doc.page_content) > 50 else doc.page_content
        logging.debug(f"Page {page_number}, {category}: {content_preview}")

    if save_image:
        plot_pdf_with_boxes(pdf_page, page_docs, file_path, output_dir)

    pdf.close()

def save_document_elements_as_json(docs, file_name, output_dir):
    """Save all document elements as a single JSON file."""
    json_file_name = os.path.splitext(file_name)[0] + '.json'
    json_file_path = os.path.join(output_dir, json_file_name)
    
    # Convert documents to a list of dictionaries
    doc_list = [
        {
            'page_number': doc.metadata.get('page_number'),
            'category': doc.metadata.get('category', 'Unknown'),
            'content': doc.page_content,
            'coordinates': doc.metadata.get('coordinates', {})
        }
        for doc in docs
    ]
    
    with open(json_file_path, 'w', encoding='utf-8') as f:
        json.dump(doc_list, f, ensure_ascii=False, indent=2)
    
    logging.info(f"Saved document elements to {json_file_path}")

# ... (keep any other existing functions)
