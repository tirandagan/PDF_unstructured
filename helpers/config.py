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
import json
from types import SimpleNamespace

# Add the GlobalConfig class
class GlobalConfig:
    def __init__(self):
        self.config = None

    def load(self, config_dict):
        self.config = json.loads(json.dumps(config_dict), object_hook=lambda d: SimpleNamespace(**d))

    def set(self, section, key, value):
        try:
            setattr(getattr(self.config, section), key, value)
        except AttributeError:
            raise KeyError(f"Section '{section}' or key '{key}' not found in configuration.")

    def get(self, section, key):
        try:
            return getattr(getattr(self.config, section), key)
        except AttributeError:
            return None

    def __str__(self):
        return str(self.config.__dict__)

# Create an instance of GlobalConfig
global_config = GlobalConfig()

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
    config = configparser.ConfigParser()
    config.read(config_path)
    
    # Read the configuration file
    config.read('config.ini')

    # Check for critical parameters
    critical_params = [
        ('API_KEYS', 'unstructured_api_key','your_unstructured_api_key_here'),
        ('API_KEYS', 'openai_api_key','your_openai_api_key_here'),
        ('DIRECTORIES', 'input_dir','./input'),
        ('DIRECTORIES', 'output_dir','./output')
    ]
    
    missing_params = []
    default_params = []
    
    for section, key, default_value in critical_params:
        if not config.has_section(section):
            config.add_section(section)
        if not config.has_option(section, key):
            config.set(section, key, default_value)
            missing_params.append(f"{section}.{key}")
    
    if missing_params:
        print(f"Critical parameter(s) missing in config.ini: {', '.join(missing_params)}")
        print("Please add the missing parameters to your config.ini file.")
        sys.exit(1)
    
    if default_params:
        print(f"The following parameter(s) in config.ini are set to default values: {', '.join(default_params)}")
        print("Please update these values in your config.ini file before running the program.")
        sys.exit(1)
    
    # Convert the configuration to a dictionary
    config_dict = {section: dict(config.items(section)) for section in config.sections()}

    # Load the config into the GlobalConfig instance
    global_config.load(config_dict)
    
    logging.debug(f"global_config set in load_config: {global_config}")
    
    # Ensure directories exist
    input_dir = global_config.get('DIRECTORIES', 'input_dir')
    output_dir = global_config.get('DIRECTORIES', 'output_dir')
    
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
    logging.debug(f"Global config contents: {global_config}")

    return global_config

def save_config():
    """Save the global configuration back to config.ini."""
    config = configparser.ConfigParser()

    # Convert the SimpleNamespace back to a dictionary
    config_dict = json.loads(json.dumps(global_config.config, default=lambda o: o.__dict__))

    for section, params in config_dict.items():
        if not config.has_section(section):
            config.add_section(section)
        for key, value in params.items():
            config.set(section, key, str(value))

    with open('config.ini', 'w') as configfile:
        config.write(configfile)
    logging.info("Configuration saved successfully to config.ini")

#-------------------------------------------------
# New get_config, used by pdf_to_jpg_converter.py
#-------------------------------------------------

def get_config(section, key, fallback=None):
    config = configparser.ConfigParser()
    config.read('config.ini')
    try:
        return config[section][key]
    except KeyError:
        return fallback

#-------------------------------------------------
# Used by original 01_pdf_to_jpg_converter.py
#-------------------------------------------------

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

# Add this at the end of the file
def get_global_config():
    global global_config
    logging.debug(f"get_global_config called, returning: {global_config}")
    return global_config
