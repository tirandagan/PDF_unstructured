import logging
import os
import pymupdf as fitz
import json

from unstructured_ingest.v2.pipeline.pipeline import Pipeline
from unstructured_ingest.v2.interfaces import ProcessorConfig
from unstructured_ingest.v2.processes.partitioner import PartitionerConfig
from unstructured_ingest.v2.processes.connectors.local import (LocalIndexerConfig, LocalDownloaderConfig, LocalConnectionConfig, LocalUploaderConfig)
from unstructured_ingest.v2.processes.connectors.local import LocalUploaderConfig
from unstructured_ingest.v2.processes.chunker import ChunkerConfig
from unstructured_ingest.v2.processes.embedder import EmbedderConfig
from .config import get_config



def ingest_pdfs(input_dir, pdf_files):
    unstructured_logger = logging.getLogger('unstructured_ingest.v2')
    current_handler = unstructured_logger.handlers[0]
    current_handler.setLevel(logging.CRITICAL)
  #  new_handler = logging.FileHandler('pdf_converter.log')
  #  new_handler.setLevel(logging.WARNING)
  #  unstructured_logger.addHandler(new_handler)

    
    show_progressbar = get_config('PDF_PROCESSING', 'SHOW_PROGRESSBAR', fallback='False').lower() == 'true'
    output_dir = os.path.realpath(get_config('DIRECTORIES', 'OUTPUT_DIR'))
    unstructured_api_key = get_config('API_KEYS', 'UNSTRUCTURED_API_KEY')
    unstructured_url = get_config('API_KEYS', "UNSTRUCTURED_URL")
    openai_api_key = get_config('API_KEYS', 'OPENAI_API_KEY')
    use_an_embedder = False

    # Embedder?
    if use_an_embedder:
        embedder_config = EmbedderConfig(
            embedding_provider="langchain-openai",
            embedding_model_name='gpt-4o',
            embedding_api_key=openai_api_key,
        )
    else:
        embedder_config = None
        
    chunker_config = ChunkerConfig(
            chunking_strategy = "by_title",
            chunk_max_characters = 1000,
            chunk_overlap = 20
        )
    chunker_config = None #<--- Remove this to add chunking
    
    Pipeline.from_configs(
        context=ProcessorConfig(
            num_processes=3,
            tqdm=show_progressbar,
        ),
        indexer_config=LocalIndexerConfig(input_path=input_dir),
        downloader_config=LocalDownloaderConfig(),
        source_connection_config=LocalConnectionConfig(),
        partitioner_config=PartitionerConfig(
            partition_by_api =True,
            strategy = "hi_res",
            api_key = unstructured_api_key,
            partition_endpoint = unstructured_url,
            extract_image_block_to_payload = True,
            additional_partition_args={
                "coordinates": True,
                "extract_image_block_types": ["Image","Table"],
                "split_pdf_page": True,
                "split_pdf_allow_failed": True,
                "split_pdf_concurrency_level": 15
            },
        ),
        chunker_config=chunker_config,
        embedder_config=embedder_config,
        uploader_config=LocalUploaderConfig(output_dir=output_dir)
    ).run()
    
def get_pdf_files(directory):
    """Get all PDF files in the specified directory."""
    return [f for f in os.listdir(directory) if f.lower().endswith('.pdf')]
    
def get_json_file_elements(pdf_filename):
    """Get the elements from the JSON file."""
    file_path = pdf_filename +'.json'
    with open(file_path, 'r') as file:
        return json.load(file)
    
