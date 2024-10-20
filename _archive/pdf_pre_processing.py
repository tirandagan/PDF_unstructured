"""
Pre-processing functions for PDF documents.

This module contains functions for pre-processing PDF files,
including counting pages and gathering file information.

Copyright © 2024 Prof. Tiran Dagan, FDU University. All rights reserved.
"""

import os
import logging
import fitz  # PyMuPDF
from langchain_unstructured import UnstructuredLoader
from unstructured_ingest.v2.pipeline.pipeline import Pipeline
from unstructured_ingest.v2.interfaces import ProcessorConfig
from unstructured_ingest.v2.processes.partitioner import PartitionerConfig
from unstructured_ingest.v2.processes.connectors.local import (LocalIndexerConfig, LocalDownloaderConfig, LocalConnectionConfig, LocalUploaderConfig)
from unstructured_ingest.v2.processes.connectors.local import LocalUploaderConfig
from unstructured_ingest.v2.processes.chunker import ChunkerConfig
from unstructured_ingest.v2.processes.embedder import EmbedderConfig

from helpers.config import get_config

def get_pdf_files(directory):
    """Get all PDF files in the specified directory."""
    return [f for f in os.listdir(directory) if f.lower().endswith('.pdf')]

def get_pdf_page_count(file_path):
    """Get the number of pages in a PDF file."""
    with fitz.open(file_path) as pdf:
        return len(pdf)

def pre_process_pdfs(input_dir):
    """Prepare PDF files for processing by counting pages and gathering file info."""
    pdf_files = get_pdf_files(input_dir)
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

def load_pdf_with_unstructured(file_path):
    """Load a PDF file using UnstructuredLoader."""
    loader = UnstructuredLoader(
        file_path=file_path,
        strategy="hi_res",
        partition_via_api=False,
        api_key=get_config('API_KEYS', 'UNSTRUCTURED_API_KEY')
    )
    
    
    return loader.load()
