import json
import os

def read_json_file(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def extract_text_to_markdown(json_data):
    markdown_content = ""
    for item in json_data:
        if 'text' in item:
            # Add a header for each text block
            markdown_content += f"## {item.get('type', 'Text Block')}\n\n"
            # Add the text content
            markdown_content += f"{item['text']}\n\n"
    return markdown_content

def save_markdown_file(content, output_file):
    with open(output_file, 'w') as file:
        file.write(content)

def main():
    # Define the input and output file paths
    input_file = "./data/output/7011-3pg.pdf.json"
    output_file = "./data/output/7011-3pg.md"

    # Check if the input file exists
    if not os.path.exists(input_file):
        print(f"Error: The file {input_file} does not exist.")
        return

    # Read the JSON file
    json_data = read_json_file(input_file)

    # Extract text and convert to markdown
    markdown_content = extract_text_to_markdown(json_data)

    # Save the markdown content to a file
    save_markdown_file(markdown_content, output_file)

    print(f"Markdown file has been created: {output_file}")

if __name__ == "__main__":
    main()
