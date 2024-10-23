"""
-----------------------------------------------------------------
(C) 2024 Prof. Tiran Dagan, FDU University. All rights reserved.
-----------------------------------------------------------------

Image Summarizer Script

This script enriches a JSON file containing image data with AI-generated summaries.
It uses OpenAI's GPT-4 Vision model to analyze and describe images based on their
base64-encoded representations. The script allows users to select a JSON file,
process its images, and save the enriched data back to the file.

Key features:
- Selects a JSON file from a specified output directory
- Summarizes images using OpenAI's GPT-4 Vision model
- Supports overriding existing summaries
- Creates a backup of the original file before processing
- Displays a progress bar during image summarization
- Handles errors gracefully and preserves original data in case of failures

Usage:
python 02_image_summarizer.py [--override]

Optional arguments:
--override: Remove existing summaries and reprocess all images
"""

import json
import os
from helpers.config import load_configuration, global_config
import inquirer
import configparser
from openai import OpenAI
from tqdm import tqdm
import argparse

current_dir = os.path.dirname(os.path.abspath(__file__))

def select_json_file(directory):
    """
    Prompts the user to select a JSON file from the specified directory.

    Args:
        directory (str): The directory to search for JSON files.

    Returns:
        str: The full path of the selected JSON file, or None if no files are found.
    """
    json_dir = os.path.abspath(directory)
    json_files = [f for f in os.listdir(json_dir) if f.endswith('.json')]
    
    if not json_files:
        print("No JSON files found in the output directory.")
        return None
    
    questions = [
        inquirer.List('file',
                      message="Select a JSON file to enrich",
                      choices=json_files,
                      carousel=True)
    ]
    answers = inquirer.prompt(questions)
    return os.path.join(directory, answers['file'])

def summarize_image(image_base64):
    """
    Generates a summary of an image using OpenAI's GPT-4 Vision model.

    Args:
        image_base64 (str): Base64-encoded image data.

    Returns:
        str: A text summary of the image content.
    """
    client = OpenAI(api_key=global_config['API_KEYS']['OPENAI_API_KEY'])
    
    prompt = """You are an image summarizing agent. I will be giving you an image and you will provide a summary describing 
    the image, starting with "An image", or "An illustration", or "A diagram:", or "A logo:" or "A symbol:". If it contains part, 
    you will try to identify the part and if it shows an action (such as a person cleaning 
    a pool or a woman holding a pool cleaning product) you will call those out. If it is a symbol, just give the symbol
    a meaningful name such as "warning symbol" or "attention!"
    """
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}"
                        }
                    }
                ]
            }
        ],
        max_tokens=300
    )
    
    return response.choices[0].message.content

def enrich_json_with_summaries(json_file, json_data):
    """
    Processes the JSON data, generating summaries for images that don't have them.

    Args:
        json_file (str): Path to the JSON file being processed.
        json_data (list): List of dictionaries containing image data.

    Returns:
        list: The enriched JSON data with added image summaries.
    """
    # Count the number of unprocessed images
    total_images = sum(1 for item in json_data if item['type'] == 'Image' and 'llm_summary' not in item)
    
    with tqdm(total=total_images, desc="Summarizing images") as pbar:
        for item in json_data:
            if item['type'] == 'Image' and 'llm_summary' not in item:
                image_base64 = item['metadata'].get('image_base64')
                if image_base64:
                    try:
                        summary = summarize_image(image_base64)
                        item['llm_summary'] = summary
                        pbar.update(1)
                        
                        # Save the file after each image is processed
                        with open(json_file, 'w', encoding='utf-8') as f:
                            json.dump(json_data, f, indent=2, ensure_ascii=False)
                    except Exception as e:
                        print(f"Error summarizing image: {str(e)}")
                else:
                    print(f"Skipping image without base64 data: {item.get('text', 'Unnamed image')}")
    
    return json_data

def remove_existing_summaries(json_data):
    """
    Removes existing 'llm_summary' fields from the JSON data.

    Args:
        json_data (list): List of dictionaries containing image data.

    Returns:
        list: The JSON data with 'llm_summary' fields removed.
    """
    for item in json_data:
        if 'llm_summary' in item:
            del item['llm_summary']
    return json_data

def main():
    """
    Main function to run the image summarization process.
    Handles command-line arguments, file selection, and error handling.
    """
    parser = argparse.ArgumentParser(description="Enrich JSON file with image summaries")
    parser.add_argument("--override", action="store_true", help="Override existing summaries")
    args = parser.parse_args()

    if not load_configuration():
        return

    output_dir = os.path.realpath(global_config['DIRECTORIES']['OUTPUT_DIR'])
    json_file = select_json_file(output_dir)
    
    if not json_file:
        return
    
    try:
        # Create a backup of the original file
        backup_file = json_file + '.bak'
        
        with open(json_file, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
            with open(backup_file, 'w', encoding='utf-8') as w:
                json.dump(json_data, w, indent=2, ensure_ascii=False)
        
        if args.override:
            json_data = remove_existing_summaries(json_data)
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)
            print("Existing summaries removed. Processing all images...")
        
        enrich_json_with_summaries(json_file, json_data)
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        print("The original file has been preserved as a backup.")
        if os.path.exists(json_file):
            os.remove(json_file)
        if os.path.exists(backup_file):
            os.rename(backup_file, json_file)

if __name__ == "__main__":
    main()
