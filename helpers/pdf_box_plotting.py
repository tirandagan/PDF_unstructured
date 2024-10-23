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
from helpers.config import get_config
from langchain_unstructured import UnstructuredLoader

# Remove or comment out the existing logging setup
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


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

def process_page(file_path, docs, page_number, save_image=False, output_dir=None):
    """
    Process a specific page of a PDF file, analyze it, and optionally save an annotated image.

    Args:
    file_path (str): Path to the PDF file.
    docs (List[Document]): List of Document objects from Langchain.
    page_number (int): The page number to process (1-indexed).
    save_image (bool): If True, save the annotated image to a file. Defaults to False.
    output_dir (str): Directory to save the annotated image.
    """
    pdf = fitz.open(file_path)
    pdf_page = pdf.load_page(page_number - 1)
    
    # Filter documents for the current page
    page_docs = [doc for doc in docs if doc.metadata.get('page_number') == page_number]
    
    # Analyze the page content (you can add more analysis here if needed)
    for doc in page_docs:
        category = doc.metadata.get('category', 'Unknown')
        content_preview = doc.page_content[:50] + "..." if len(doc.page_content) > 50 else doc.page_content
        logging.debug(f"Page {page_number}, {category}: {content_preview}")

    if save_image:
        plot_pdf_with_boxes(pdf_page, page_docs, file_path, output_dir)

    pdf.close()

def process_pdf(file_path: str, num_pages: int, save_images: bool, output_dir: str, progress_bar):
    """Load, process, and analyze a PDF document with progress tracking."""
    file_name = os.path.basename(file_path)
    
    # Pre-Processing phase
    progress_bar.text(f"Pre-Processing: {file_name}")
    loader = UnstructuredLoader(
        file_path=file_path,
        strategy="hi_res",
        partition_via_api=True,
        coordinates=True,
        api_key=get_config('API_KEYS', 'UNSTRUCTURED_API_KEY')
    )
    docs = loader.load()
    
    logging.info(f"Number of documents in {file_name}: {len(docs)}")
    logging.info(f"Number of pages in {file_name}: {num_pages}")

    # Analyzing Pages phase
    progress_bar.text(f"Analyzing Pages: {file_name}")
    for page_number in range(1, num_pages + 1):
        progress_bar.text(f"Analyzing {file_name}: page {page_number}/{num_pages}")
        process_page(file_path, docs, page_number, save_image=save_images, output_dir=output_dir)
        progress_bar()

    return docs

def get_pdf_page_count(file_path):
    """Get the number of pages in a PDF file."""
    with fitz.open(file_path) as pdf:
        return len(pdf)

# Add this line at the end of the file
__all__ = ['plot_pdf_with_boxes', 'process_pdf', 'get_pdf_page_count']