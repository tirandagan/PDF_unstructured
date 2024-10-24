"""
PDF Annotation and Visualization Tool (Unstructured.io API version)

This module provides functionality to annotate and visualize PDF pages with bounding boxes
around different types of content (text, titles, images, tables) using the Unstructured.io API.
It uses the PyMuPDF (fitz) library for PDF handling and Matplotlib for visualization.

Copyright © 2024 Prof. Tiran Dagan, FDU University. All rights reserved.
Source: https://python.langchain.com/docs/how_to/document_loader_pdf/

Main components:
1. plot_pdf_with_boxes: Renders a PDF page with annotated bounding boxes for different content types.
2. render_page: Processes a specific page of a PDF, annotates it, and optionally prints the text content.
3. process_pdf: Loads and processes an entire PDF document with progress tracking.

Dependencies:
- fitz (PyMuPDF)
- matplotlib
- Pillow (PIL)
- unstructured_client (for Unstructured.io API)
- langchain_unstructured
"""

import fitz
import matplotlib.patches as patches
import matplotlib.pyplot as plt
from PIL import Image
import os
import logging
from typing import List
import numpy as np
from .config import global_config
from .pdf_ingest import get_json_file_elements

# Remove or comment out the existing logging setup
#logging.basicConfig(level=logging.WARNING)
#logger = logging.getLogger(__name__)


def plot_pdf_with_boxes(pdf_page, documents, output_filename, output_dir):
    """
    Annotate a PDF page with bounding boxes for different content types and save as an image.

    Args:
    pdf_page (fitz.Page): A PyMuPDF page object.
    documents (List[Document]): List of Document objects from Langchain.
    output_filename (str): Name of the output file.
    output_dir (str): Directory to save the annotated image.
    """
    pix = pdf_page.get_pixmap()
    pil_image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

    fig, ax = plt.subplots(1, figsize=(20, 20))  # Large figure size for clarity
    ax.imshow(pil_image)
    
    category_to_color = {
        "Title": "orchid",
        "Image": "forestgreen",
        "Table": "tomato",
        "ListItem": "gold",
        "NarrativeText": "deepskyblue",
    }
    
    boxes_drawn = 0
    for doc in documents:
        category = doc['type']

        c=doc['metadata']['coordinates']
        
        points = c['points']
        layout_width = c['layout_width']
        layout_height = c['layout_height']

        scaled_points = [
            (x * pix.width / layout_width, y * pix.height / layout_height)
            for x, y in points
        ]
        box_color = category_to_color.get(category, "deepskyblue")
        polygon = patches.Polygon(
            scaled_points, linewidth=2, edgecolor=box_color, facecolor="none"
        )
        ax.add_patch(polygon)
        boxes_drawn += 1
    
    
    legend_handles = [patches.Patch(color=color, label=category) for category, color in category_to_color.items()]
    ax.axis("off")
    ax.legend(handles=legend_handles, loc="upper right")
    plt.tight_layout()

    base_filename = os.path.splitext(os.path.basename(output_filename))[0]
    complete_image_path = os.path.join(output_dir, f"{base_filename}-{pdf_page.number + 1}-annotated.jpg")
    os.makedirs(output_dir, exist_ok=True)  # Ensure the output directory exists
    fig.savefig(complete_image_path, format="jpg", dpi=300)  # High DPI for quality
    plt.close(fig)

    logging.info(f"Annotated {boxes_drawn} boxes on page {pdf_page.number + 1}: saved as: {complete_image_path}")


def get_pdf_page_count(file_path):
    """Get the number of pages in a PDF file."""
    with fitz.open(file_path) as pdf:
        return len(pdf)

def process_pdf_pages(file_name: str, num_pages: int, progress_bar):

    """
    Process the pages of a PDF file, creating an annotated image for each page.

    Args:
    file_path (str): Path to the PDF file.
    docs (List[Document]): List of Document objects from Langchain.
    save_image (bool): If True, save the annotated image to a file. Defaults to False.
    output_dir (str): Directory to save the annotated image.
    
    """
    output_dir = global_config.get('DIRECTORIES', 'output_dir')
    input_dir = global_config.get('DIRECTORIES', 'input_dir')
    
    input_json_path = os.path.join(output_dir,file_name ) # fetch the json file elements for the document
    input_file_path = os.path.join(input_dir,file_name)
    
    pdf = fitz.open(input_file_path)
    docs = get_json_file_elements(input_json_path)
    
    progress_bar.text(f"Analyzing Pages: {file_name}")
    for page_number in range(1, num_pages + 1):
        progress_bar.text(f"Analyzing {input_file_path}: page {page_number}/{num_pages}")
        progress_bar()
        plot_pdf_with_boxes(pdf.load_page(page_number - 1), docs, input_file_path, output_dir)
        
    pdf.close()
