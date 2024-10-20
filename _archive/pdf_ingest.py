"""
PDF Ingestion and Processing Module for LangChain PDF Analyzer

This module provides functions to ingest, process, and analyze PDF documents using LangChain's UnstructuredLoader.
It extracts text and metadata from PDFs, categorizes document elements, and optionally creates visualizations.

Copyright © 2024 Prof. Tiran Dagan, FDU University. All rights reserved.

Main functionalities:
1. Ingest multiple PDF files using UnstructuredLoader
2. Extract and categorize document elements (text, titles, images, tables)
3. Save processed data as JSON files
4. Create bounding box visualizations of document elements (optional)

Dependencies:
- langchain
- unstructured
- PIL (Pillow)
- matplotlib
- json
- alive_progress

Usage:
Call ingest_pdfs() to process a list of PDF files and extract their content.
Use create_bbox_images() to generate visualizations of document elements.
"""

import os
import json
from langchain_community.document_loaders import UnstructuredLoader
from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt
from alive_progress import alive_bar
import logging

from .config import get_config

def ingest_pdfs(input_dir, pdf_files):
    """
    Ingest and process multiple PDF files.
    
    Args:
        input_dir (str): Directory containing the PDF files.
        pdf_files (list): List of PDF filenames to process.
    
    Returns:
        list: List of dictionaries containing processed document elements for each PDF.
    """
    results = []
    with alive_bar(len(pdf_files), title="Processing PDFs", bar="classic") as bar:
        for pdf_file in pdf_files:
            pdf_path = os.path.join(input_dir, pdf_file)
            loader = UnstructuredLoader(pdf_path)
            elements = loader.load()
            
            processed_elements = process_elements(elements)
            results.append({"filename": pdf_file, "elements": processed_elements})
            
            save_as_json(processed_elements, pdf_file)
            bar()
    
    return results

def process_elements(elements):
    """
    Process and categorize document elements extracted from a PDF.
    
    Args:
        elements (list): Raw document elements from UnstructuredLoader.
    
    Returns:
        list: Processed and categorized document elements.
    """
    processed_elements = []
    for element in elements:
        processed_element = {
            "type": element.type,
            "text": element.text,
            "metadata": element.metadata
        }
        processed_elements.append(processed_element)
    return processed_elements

def save_as_json(processed_elements, pdf_file):
    """
    Save processed document elements as a JSON file.
    
    Args:
        processed_elements (list): Processed document elements.
        pdf_file (str): Name of the original PDF file.
    """
    output_dir = get_config('DIRECTORIES', 'OUTPUT_DIR')
    output_path = os.path.join(output_dir, f"{pdf_file}.json")
    with open(output_path, 'w') as f:
        json.dump(processed_elements, f, indent=2)

def create_bbox_images(input_dir, pdf_files):
    """
    Create bounding box visualizations for processed PDF documents.
    
    Args:
        input_dir (str): Directory containing the original PDF files.
        pdf_files (list): List of PDF filenames to visualize.
    """
    output_dir = get_config('DIRECTORIES', 'OUTPUT_DIR')
    bbox_dir = os.path.join(output_dir, 'bbox_images')
    os.makedirs(bbox_dir, exist_ok=True)

    with alive_bar(len(pdf_files), title="Creating Bounding Box Images", bar="classic") as bar:
        for pdf_file in pdf_files:
            json_path = os.path.join(output_dir, f"{pdf_file}.json")
            with open(json_path, 'r') as f:
                elements = json.load(f)
            
            create_bbox_image_for_pdf(elements, pdf_file, bbox_dir)
            bar()

def create_bbox_image_for_pdf(elements, pdf_file, bbox_dir):
    """
    Create a bounding box visualization for a single PDF document.
    
    Args:
        elements (list): Processed document elements.
        pdf_file (str): Name of the original PDF file.
        bbox_dir (str): Directory to save the visualization.
    """
    # Implementation details for creating bounding box images
    # (This function would contain the logic to draw bounding boxes on page images)
    pass

# Additional helper functions for PDF processing can be added here
