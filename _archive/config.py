"""
Configuration Loader for LangChain PDF Analyzer

This module provides functions to load and access configuration settings for the LangChain PDF Analyzer application.
It reads settings from a 'config.ini' file and makes them available throughout the application.

Copyright © 2024 Prof. Tiran Dagan, FDU University. All rights reserved.

Main functionalities:
1. Load configuration settings from 'config.ini'
2. Provide access to configuration values
3. Handle configuration errors and missing values

Dependencies:
- configparser

Usage:
Call load_configuration() at the start of the application to initialize the configuration.
Use get_config(section, key) to retrieve specific configuration values.
"""

import configparser
import os
import logging

# Initialize the configuration parser
config = configparser.ConfigParser()

def load_configuration():
    """
    Load the configuration from the 'config.ini' file.
    
    Returns:
        bool: True if configuration is successfully loaded, False otherwise.
    """
    config_path = 'config.ini'
    if not os.path.exists(config_path):
        logging.error(f"Configuration file '{config_path}' not found.")
        return False
    
    config.read(config_path)
    
    # Validate required sections and keys
    required_sections = ['API_KEYS', 'DIRECTORIES', 'PDF_PROCESSING']
    for section in required_sections:
        if section not in config:
            logging.error(f"Missing required section '{section}' in config.ini")
            return False
    
    # Additional validation can be added here
    
    return True

def get_config(section, key):
    """
    Retrieve a specific configuration value.
    
    Args:
        section (str): The section name in the configuration file.
        key (str): The key name within the section.
    
    Returns:
        str: The configuration value if found, None otherwise.
    """
    try:
        return config[section][key]
    except KeyError:
        logging.error(f"Configuration key '{key}' not found in section '{section}'")
        return None

# Additional helper functions for configuration management can be added here
