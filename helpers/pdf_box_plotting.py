"""
-----------------------------------------------------------------
(C) 2024 Prof. Tiran Dagan, FDU University. All rights reserved.
-----------------------------------------------------------------

PDF Annotation and Visualization Tool (Unstructured.io API version)

This module provides functionality to annotate and visualize PDF pages with bounding boxes
around different types of content (text, titles, images, tables) using the Unstructured.io API.
It uses the PyMuPDF (fitz) library for PDF handling and Matplotlib for visualization.

Key features:
- Annotate PDF pages with bounding boxes
- Visualize content types with different colors
- Save annotated pages as images

Usage:
- Use `plot_pdf_with_boxes()` to annotate and save a PDF page as an image.
- Use `process_pdf_pages()` to process and annotate all pages in a PDF.
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
from .display import update_log_window

def plot_pdf_with_boxes(pdf_page, documents, output_filename, output_dir):
    """
    Annotate a PDF page with bounding boxes for different content types and save as an image.

    Args:
        pdf_page (fitz.Page): A PyMuPDF page object.
        documents (List[Document]): List of Document objects from Langchain.
        output_filename (str): Name of the output file.
        output_dir (str): Directory to save the annotated image.
    """
    logging.basicConfig(filename='pdf_converter.log', level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')

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

    logging.info(f"{boxes_drawn} annotations on page {pdf_page.number + 1} of: {base_filename}")

def get_pdf_page_count(file_path):
    """
    Get the number of pages in a PDF file.

    Args:
        file_path (str): Path to the PDF file.

    Returns:
        int: The number of pages in the PDF.
    """
    with fitz.open(file_path) as pdf:
        return len(pdf)

def process_pdf_pages(stdcr, file_name: str, num_pages: int, progress_bar):
    """
    Process the pages of a PDF file, creating an annotated image for each page.

    Args:
        file_name (str): Name of the PDF file.
        num_pages (int): Total number of pages in the PDF.
        progress_bar: Function to update the progress bar.
    """
    output_dir = global_config.get('DIRECTORIES', 'output_dir')
    input_dir = global_config.get('DIRECTORIES', 'input_dir')
    
    input_json_path = os.path.join(output_dir, file_name)  # Fetch the JSON file elements for the document
    input_file_path = os.path.join(input_dir, file_name)
    
    pdf = fitz.open(input_file_path)
    docs = get_json_file_elements(input_json_path)
    
    progress_bar.text(f"Analyzing Pages: {file_name}")
    for page_number in range(1, num_pages + 1):
        progress_bar.text(f"Analyzing {input_file_path}: page {page_number}/{num_pages}")
        progress_bar()
        
        # Filter documents for the current page
        page_docs = [doc for doc in docs if doc['metadata'].get('page_number') == page_number]
        
        plot_pdf_with_boxes(pdf.load_page(page_number - 1), page_docs, input_file_path, output_dir)
        update_log_window(stdcr)
    pdf.close()
