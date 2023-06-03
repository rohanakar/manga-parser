import argparse
import os
import logging
import configparser

import logging.config
import os

from jobs.subjobs.process_images import process_images
from utils import fileutils

# Import the logging configuration from the logging_config module
logger = logging.getLogger(__name__)
def initialize_folders(folders):
    fileutils.create_folders(folders)

def main():
     # Read default values from the configuration file
    config = configparser.ConfigParser()
    config.read('config/app.ini')

    default_values = config["DEFAULT"]
    sound_values = config["SOUND"]

    parser = argparse.ArgumentParser(description="Initialize folders CLI utility")

    parser.add_argument("--inbox_folder", default=default_values.get("inbox_folder"), help="Folder path for inbox")
    parser.add_argument("--processing_folder", default=default_values.get("processing_folder"), help="Folder path for processing")
    parser.add_argument("--processed_folder", default=default_values.get("processed_folder"), help="Folder path for processed")
    parser.add_argument("--ost_folder", default=sound_values.get("ost_folder"), help="Folder for OST")

    args = parser.parse_args()

    # Convert args namespace to a dictionary
    arguments = vars(args)

    initialize_folders([arguments[key] for key in ['inbox_folder','processing_folder','processed_folder','ost_folder']])
    
if __name__ == "__main__":
    main()
