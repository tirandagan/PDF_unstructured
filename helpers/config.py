"""
Helper functions for configuration and environment setup.

This module provides utility functions for loading configuration,
setting up a global config object, and handling API key prompts.

Copyright © 2024 Prof. Tiran Dagan, FDU University. All rights reserved.
"""

import configparser
import logging
import os
import sys

# Global config object
global_config = configparser.ConfigParser()

DEFAULT_CONFIG = """
[API_KEYS]
UNSTRUCTURED_API_KEY = your_unstructured_api_key_here
OPENAI_API_KEY = your_openai_api_key_here

[DIRECTORIES]
INPUT_DIR = ./input
OUTPUT_DIR = ./output

[PDF_PROCESSING]
SAVE_IMAGES = True
SAVE_DOCUMENT_ELEMENTS = True
"""

def create_default_config(config_path):
    """Create a default config.ini file."""
    with open(config_path, 'w') as config_file:
        config_file.write(DEFAULT_CONFIG)
    logging.info(f"Created default config file at {config_path}")

def load_config(config_path='config.ini'):
    """Load configuration from config.ini file."""
    global global_config
    
    if not os.path.exists(config_path):
        logging.warning(f"Config file not found at {config_path}. Creating default config.")
        create_default_config(config_path)
        print(f"A default configuration file has been created at {config_path}")
        print("Please edit this file to add your API keys before running the program again.")
        sys.exit(1)
    
    global_config.read(config_path)
    
    # Check for critical parameters
    critical_params = [
        ('API_KEYS', 'UNSTRUCTURED_API_KEY'),
        ('API_KEYS', 'OPENAI_API_KEY'),
        ('DIRECTORIES', 'INPUT_DIR'),
        ('DIRECTORIES', 'OUTPUT_DIR')
    ]
    
    missing_params = []
    default_params = []
    
    for section, key in critical_params:
        if not global_config.has_option(section, key) or not global_config.get(section, key):
            missing_params.append(f"{section}.{key}")
        elif global_config.get(section, key) in ['your_unstructured_api_key_here', 'your_openai_api_key_here']:
            default_params.append(f"{section}.{key}")
    
    if missing_params:
        print(f"Critical parameter(s) missing in config.ini: {', '.join(missing_params)}")
        print("Please add the missing parameters to your config.ini file.")
        sys.exit(1)
    
    if default_params:
        print(f"The following parameter(s) in config.ini are set to default values: {', '.join(default_params)}")
        print("Please update these values in your config.ini file before running the program.")
        sys.exit(1)
    
    # Ensure directories exist
    input_dir = global_config.get("DIRECTORIES", "INPUT_DIR")
    output_dir = global_config.get("DIRECTORIES", "OUTPUT_DIR")
    
    if input_dir:
        os.makedirs(input_dir, exist_ok=True)
        logging.info(f"Ensured input directory exists: {input_dir}")
    else:
        logging.error("INPUT_DIR not found in configuration")
    
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        logging.info(f"Ensured output directory exists: {output_dir}")
    else:
        logging.error("OUTPUT_DIR not found in configuration")
    
    logging.info("Configuration loaded successfully")
    logging.debug(f"Global config contents: {dict(global_config)}")

    return global_config

def get_config(section, key):
    """Get a specific configuration value."""
    return global_config.get(section, key, fallback=None)

def load_configuration():
    """Load and validate the configuration."""
    try:
        config = load_config()
        logging.debug(f"Loaded config: {dict(config)}")
        return config
    except SystemExit:
        logging.error("Configuration error. Exiting program.")
        return None
    except Exception as e:
        logging.error(f"Unexpected error during configuration: {e}")
        return None

