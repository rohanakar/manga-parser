import argparse
import configparser
import os
import logging
from jobs.subjobs.intitalize import initialize_folders
from utils import fileutils

import logging.config
import os
from jobs.subjobs.merge import merge_video_files

from jobs.subjobs.process_images import process_images

# Import the logging configuration from the logging_config module
logger = logging.getLogger(__name__)

def process_inbox(arguments):
    logger.debug("Processing inbox...")
    logger.info(arguments)
    # # Your processing logic here
    logger.info('initializing folders')

    initialize_folders([arguments[key] for key in ['inbox_folder','processing_folder','processed_folder','ost_folder']])
    
    logger.info('processing images and generating metadata')
    
    process_images(arguments[key] for key in ['inbox_folder','processing_folder','tts_enabled'])

    processing_folder = arguments['processing_folder']
    processed_folder = arguments['processed_folder']
    tts = arguments['tts_enabled']
    folders_name = [folder for folder in fileutils.list_folders(processing_folder)]
    for folder in folders_name:
        folder_name = fileutils.get_relative_path(processing_folder,folder,str(tts))
        file_name = fileutils.get_relative_path(processed_folder,folder+"-"+str(tts)+".mp4")
        merge_video_files([folder_name,file_name,])

    
def main():
    # Read default values from the configuration file
    config = configparser.ConfigParser()
    config.read('config/app.ini')

    default_values = config["DEFAULT"]
    sound_values = config["SOUND"]
    parser = argparse.ArgumentParser(description="Batch Job CLI Application")

    parser.add_argument("--inbox_folder", default=default_values.get("inbox_folder"), help="Folder path for inbox")
    parser.add_argument("--processing_folder", default=default_values.get("processing_folder"), help="Folder path for processing")
    parser.add_argument("--processed_folder", default=default_values.get("processed_folder"), help="Folder path for processed")
    parser.add_argument("--tts_enabled", default=default_values.getboolean("tts_enabled"), help="Enable text-to-speech")
    parser.add_argument("--ost_folder", default=sound_values.get("ost_folder"), help="Folder for OST")

   
    args = parser.parse_args()

    # Convert args namespace to a dictionary
    arguments = vars(args)
    if(arguments['tts_enabled'] == 'True'):
        arguments['tts_enabled'] = True
    if(arguments['tts_enabled'] == 'False'):
        arguments['tts_enabled'] = False
    
    # Print thep current configuration
    process_inbox(arguments)

if __name__ == "__main__":
    main()
