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
            # Add GitHub-style quote for important information
            if "important" in content.lower():
                markdown_content += f"> [!IMPORTANT]\n> {content}\n\n"
            elif "note" in content.lower():
                markdown_content += f"> [!NOTE]\n> {content}\n\n"
            elif "warning" in content.lower():
                markdown_content += f"> [!WARNING]\n> {content}\n\n"
            else:
                markdown_content += f"{content}\n\n"
        elif category == 'ListItem':
            # Convert to task list if it starts with "TODO" or "TASK"
            if content.lower().startswith(("todo", "task")):
                markdown_content += f"- [ ] {content}\n"
            else:
                markdown_content += f"- {content}\n"
        elif category == 'Table':
            # Add a collapsible section for tables
            markdown_content += "<details>\n<summary>Table</summary>\n\n"
            markdown_content += item['metadata'].get('text_as_html', '') + "\n"
            markdown_content += "</details>\n\n"
        elif category == 'Image':
            image_base64 = item['metadata']['image_base64']
            if image_base64:
                # Use GitHub's theme-specific image display
                image_format = 'png' if image_base64.startswith('/9j/') else 'jpeg'
                summary = item['llm_summary']
                markdown_content += f"<picture>\n"
                markdown_content += f"  <source media=\"(prefers-color-scheme: dark)\" srcset=\"data:image/{image_format};base64,{image_base64}\">\n"
                markdown_content += f"  <source media=\"(prefers-color-scheme: light)\" srcset=\"data:image/{image_format};base64,{image_base64}\">\n"
                markdown_content += f"  <img alt=\"{summary}\" src=\"data:image/{image_format};base64,{image_base64}\">\n"
                markdown_content += f"</picture>\n\n"
                markdown_content += f"*{summary}*\n\n"
            else:
                markdown_content += f"> Image: **{content or '?Unknown'}**\n\n"
        else:
            # Wrap unknown content types in collapsible sections
            markdown_content += f"<details>\n<summary>{category}</summary>\n\n{content}\n\n</details>\n\n"
    
    # Add a table of contents at the beginning
    toc = "## Table of Contents\n\n"
    for item in json_data:
        if item.get('type') == 'Title':
            toc += f"- [{item['text']}](#{item['text'].lower().replace(' ', '-')})\n"
    
    return toc + "\n---\n\n" + markdown_content

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
