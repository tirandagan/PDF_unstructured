# To use this program
# pip install inquirer pandas tabulate

import json
import os
import inquirer
from tabulate import tabulate
import pandas as pd
from helpers.config import load_configuration, global_config

current_dir = os.path.dirname(os.path.abspath(__file__))

def select_json_file(directory): 

    # Create the output directory path relative to the script location
    json_dir = os.path.abspath(os.path.join(current_dir, directory))


    json_files = [f for f in os.listdir(json_dir) if f.endswith('.json')]
    if not json_files:
        print("No JSON files found in the output directory.")
        return None
    
    questions = [
        inquirer.List('file',
                      message="Select a JSON file to convert",
                      choices=json_files,
                      carousel=True)
    ]
    answers = inquirer.prompt(questions)
    return os.path.join(directory, answers['file'])

def convert_table_to_markdown(content):
    try:
        # Assuming the content is a string representation of a list of lists
        table_data = eval(content)
        df = pd.DataFrame(table_data[1:], columns=table_data[0])
        return tabulate(df, headers='keys', tablefmt='pipe', showindex=False)
    except:
        return f"<Unable to parse table content: {content}>"

def json_to_markdown(json_data):
    markdown_content = "\n"
    
    for item in json_data:
        category = item.get('type', 'Unknown')
        content = item.get('text', '')
        
        if category == 'Title':
            markdown_content += f"# {content}\n\n"
        elif category == 'NarrativeText':
            markdown_content += f"{content}\n\n"
        elif category == 'ListItem':
            markdown_content += f"- {content}\n"
        elif category == 'Table':
            markdown_content +=  item['metadata'].get('text_as_html', '') + "\n\n"           
        elif category == 'Image':
            image_base64 = item['metadata']['image_base64']
            if image_base64:
                # Determine the image format (assuming it's either PNG or JPEG)
                image_format = 'png' if image_base64.startswith('/9j/') else 'jpeg'
                summary = item['llm_summary']
                image_tag = f"![IMAGE:](data:image/{image_format};base64,{image_base64})"
                markdown_content += f"| {image_tag}  |\n|:--:|\n| *{summary}* |\n\n"
            else:
                markdown_content += f"> Image: {content or '?Unknown'}\n\n"
        else:
            markdown_content += f"{content}\n\n"
    
    return markdown_content

def main():
    if not load_configuration():
        return
    
    output_dir = os.path.realpath(global_config['DIRECTORIES']['OUTPUT_DIR'])
    json_file = select_json_file(output_dir)
    if not json_file:
        return
    
    with open(json_file, 'r', encoding='utf-8') as f:
        json_data = json.load(f)
    
    markdown_content = json_to_markdown(json_data)
    
    markdown_file = os.path.splitext(json_file)[0] + '.md'
    with open(markdown_file, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    print(f"Markdown file created: {markdown_file}")

if __name__ == "__main__":
    main()
