import tqdm
from openai import OpenAI
import json
from .config import global_config
import curses
from .display import get_window_info

def enrich_json_with_summaries(stdscr, json_file, json_data):
    """
    Processes the JSON data, generating summaries for images that don't have them.
    Displays progress for pages and images.

    Args:
        stdscr: The curses screen object.
        json_file (str): Path to the JSON file being processed.
        json_data (list): List of dictionaries containing image data.

    Returns:
        list: The enriched JSON data with added image summaries.
    """
    # Count the number of unprocessed images
    total_images = sum(1 for item in json_data if item['type'] == 'Image' and 'llm_summary' not in item)
    current_image = 0

    # Get writable coordinates for the "File Progress" window
    top, left, bottom, right = get_window_info("File Progress", stdscr)
    progress_win_height = bottom - top
    progress_win_width = right - left

    def update_progress_bar(page_number, total_pages, image_number, total_images):
        progress_win = curses.newwin(progress_win_height, progress_win_width, top, left)
        progress_win.bkgd(' ', curses.color_pair(3))
        progress_win.box()
        progress_win.addstr(0, 2, "File Progress", curses.A_REVERSE)

        # Page progress bar
        page_progress = int((page_number / total_pages) * (progress_win_width - 12))
        page_bar_str = f"[{'#' * page_progress}{' ' * ((progress_win_width - 12) - page_progress)}]"
        progress_win.addstr(1, 2, f"Enhancing Page {page_number}/{total_pages}", curses.color_pair(3))
        progress_win.addstr(2, 2, page_bar_str)

        # Horizontal line separator
        progress_win.hline(3, 1, curses.ACS_HLINE, progress_win_width - 2)

        # Image progress bar
        image_progress = int((image_number / total_images) * (progress_win_width - 12))
        image_bar_str = f"[{'#' * image_progress}{' ' * ((progress_win_width - 12) - image_progress)}]"
        progress_win.addstr(4, 2, f"Image {image_number}/{total_images}", curses.color_pair(3))
        progress_win.addstr(5, 2, image_bar_str)

        progress_win.refresh()

    total_pages = len(set(item['metadata'].get('page_number') for item in json_data if item['type'] == 'Image'))
    current_page = 0

    for page_number in range(1, total_pages + 1):
        page_images = [item for item in json_data if item['type'] == 'Image' and item['metadata'].get('page_number') == page_number]
        total_page_images = len(page_images)
        current_page += 1

        for item in page_images:
            if 'llm_summary' not in item:
                current_image += 1
                update_progress_bar(current_page, total_pages, current_image, total_images)

                image_base64 = item['metadata'].get('image_base64')
                if image_base64:
                    try:
                        summary = summarize_image(image_base64)
                        item['llm_summary'] = summary

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

def summarize_image(image_base64):
    """
    Generates a summary of an image using OpenAI's GPT-4 Vision model.

    Args:
        image_base64 (str): Base64-encoded image data.

    Returns:
        str: A text summary of the image content.
    """
    client = OpenAI(api_key=global_config.get('API_KEYS', 'openai_api_key'))
    
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
