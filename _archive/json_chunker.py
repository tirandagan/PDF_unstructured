###
# Not working properly
###

import json
import os
import inquirer
from unstructured_ingest.v2.pipeline.pipeline import Pipeline
from unstructured_ingest.v2.interfaces import ProcessorConfig
from unstructured_ingest.v2.processes.connectors.local import (
    LocalIndexerConfig,
    LocalDownloaderConfig,
    LocalConnectionConfig,
    LocalUploaderConfig
)
from unstructured_ingest.v2.processes.partitioner import PartitionerConfig
from unstructured_ingest.v2.processes.chunker import ChunkerConfig

def select_json_file(directory):
    json_files = [f for f in os.listdir(directory) if f.endswith('.json')]
    if not json_files:
        print("No JSON files found in the output directory.")
        return None
    
    questions = [
        inquirer.List('file',
                      message="Select a JSON file to chunk",
                      choices=json_files,
                      carousel=True)
    ]
    answers = inquirer.prompt(questions)
    return os.path.join(directory, answers['file'])

def chunk_json_file(input_file, output_file):
    # Run the chunking pipeline
    Pipeline.from_configs(
        context=ProcessorConfig(),
        indexer_config=LocalIndexerConfig(input_path=os.path.dirname(input_file)),
        downloader_config=LocalDownloaderConfig(),
        source_connection_config=LocalConnectionConfig(),
        partitioner_config=PartitionerConfig(
            partition_by_api=False,  # We don't need to partition again
        ),
        chunker_config=ChunkerConfig(
            chunking_strategy="by_title",
            chunk_max_characters=1024
        ),
        uploader_config=LocalUploaderConfig(output_dir=os.path.dirname(output_file))
    ).run()

    # Rename the output file to match the desired name
    chunked_file = os.path.join(os.path.dirname(output_file), os.path.basename(input_file))
    if os.path.exists(chunked_file):
        os.rename(chunked_file, output_file)
    else:
        raise FileNotFoundError(f"Expected chunked file not found: {chunked_file}")

def main():
    # Get the directory of the current script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Create the output directory path relative to the script location
    output_dir = os.path.abspath(os.path.join(current_dir, '../data/output'))
    
    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    json_file = select_json_file(output_dir)
    
    if not json_file:
        return
    
    # Get the base name without extension
    base_name = os.path.splitext(os.path.basename(json_file))[0]
    
    # Create the output filename with a different name
    output_file = os.path.join(output_dir, f"{base_name}-chunked.json")
    
    try:
        chunk_json_file(json_file, output_file)
        print(f"Chunked JSON file created: {output_file}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
