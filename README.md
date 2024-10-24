# Unstructured.io PDF Processing and Analysis Suite

This project consists of three main applications that work together to process, analyze, and enrich PDF documents using Unstructured.io and various AI technologies.

## Applications Overview

### 1. PDF Ingestion (01_ingest_pdf.py)

This script uses Unstructured.io's UnstructuredLoader to process and analyze PDF documents.

Key features:
- Loads and parses multiple PDF documents
- Extracts text and metadata from PDFs
- Analyzes and categorizes document elements (e.g., text, titles, images, tables)
- Optionally visualizes the document structure
- Displays progress across files and pages

Input: PDF files in the specified input directory
Output: JSON files containing structured data from the PDFs, saved in the output directory

### 2. Image Summarization (02_image_summarizer.py)

This script enriches the JSON files generated by the PDF ingestion step by adding AI-generated summaries for images.

Key features:
- Selects a JSON file to process
- Uses OpenAI's GPT-4 Vision model to generate summaries for images
- Adds summaries to the JSON data
- Provides an option to override existing summaries

Input: JSON files generated by 01_ingest_pdf.py
Output: Enriched JSON files with image summaries

### 3. Markdown Conversion (03_output_markdown.py)

This script converts the enriched JSON files into human-readable Markdown format.

Key features:
- Selects a JSON file to convert
- Transforms structured JSON data into formatted Markdown
- Includes image summaries and base64-encoded images in the Markdown output

Input: Enriched JSON files from 02_image_summarizer.py
Output: Markdown files containing the formatted content of the PDFs

## Prerequisites

- Python 3.11 or higher (but lower than 3.13)
- Poetry (for package management and virtual environment)

## Installation

### 1. Install Poetry (if not already installed)

If you don't have Poetry installed, follow these steps:

#### On macOS or Windows (WSL):

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

#### On Linux:

```bash
# Make sure you have python3-venv installed
sudo apt-get install python3-venv

# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -
```

#### On Windows (PowerShell):

```powershell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
```

After installation, restart your terminal or run `source $HOME/.poetry/env` to add Poetry to your PATH.

### 2. Clone the repository:

```bash
git clone https://github.com/tirandagan/PDF_unstructured.git
cd PDF_unstructured
```

### 3. Set up the project:

```bash
# Install dependencies
poetry install

# Activate the virtual environment
poetry shell
```

### 4. Set up the `config.ini` file:
- Rename `config.ini.template` to `config.ini`
- Open `config.ini` and fill in the necessary API keys and directory paths

## Usage

### 1. PDF Ingestion (01_ingest_pdf.py)

1. Place PDF files in the input directory specified in `config.ini`
2. Run the script:
   ```
   python 01_ingest_pdf.py
   ```
3. The script will process all PDF files and generate JSON output files in the specified output directory

### 2. Image Summarization (02_image_summarizer.py)

1. Ensure you have run 01_ingest_pdf.py and have JSON files in the output directory
2. Run the script:
   ```
   python 02_image_summarizer.py
   ```
3. Select the JSON file you want to enrich from the interactive prompt
4. The script will process all images in the selected JSON file and add summaries
5. To override existing summaries, use the `--override` flag:
   ```
   python 02_image_summarizer.py --override
   ```

### 3. Markdown Conversion (03_output_markdown.py)

1. Ensure you have run 02_image_summarizer.py and have enriched JSON files
2. Run the script:
   ```
   python 03_output_markdown.py
   ```
3. Select the JSON file you want to convert from the interactive prompt
4. The script will generate a Markdown file with the same name as the input JSON file

## Data Flow

1. PDF files → 01_ingest_pdf.py → JSON files with structured data
2. JSON files → 02_image_summarizer.py → Enriched JSON files with image summaries
3. Enriched JSON files → 03_output_markdown.py → Formatted Markdown files

## Configuration

The `config.ini` file contains important settings:

- API keys for OpenAI
- Input and output directory paths
- Other processing options

To set up your configuration:

1. Locate the `config.ini.template` file in the project directory
2. Rename `config.ini.template` to `config.ini`
3. Open `config.ini` in a text editor
4. Fill in your specific API keys, directory paths, and other settings
5. Save the file

Ensure this file is properly configured before running the scripts. The `config.ini` file is excluded from version control to protect sensitive information, so you'll need to set it up locally.

## License

Copyright © 2024 Prof. Tiran Dagan, FDU University. All rights reserved.
