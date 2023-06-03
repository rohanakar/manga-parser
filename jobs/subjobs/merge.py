import argparse
import logging
import configparser

import logging.config
from domain.manga import Manga
from jobs.subjobs.process_image import process_image_and_write_video_metadata
from services import video_generation_service
from utils import database, fileutils 

# Import the logging configuration from the logging_config module
logger = logging.getLogger(__name__)

config = configparser.ConfigParser()
config.read('config/app.ini')
default_values = config["DEFAULT"]

def update_status(curr,tts):
    bit_0 = curr%2
    bit_1 = (curr//2)%2
    if tts == 'True':
        bit_0 = 1
    if tts == 'False':
        bit_1 = 1
    return bit_0+(bit_1*2)

def merge_video_files(arguments):
    input_folder,output_file = arguments
    logger.debug(f'merge files from {input_folder} to {output_file}')
    try:
        files = sorted([fileutils.get_relative_path(input_folder,file) for file in fileutils.get_files(input_folder) if file.endswith('mp4')])
        logger.debug(f'merging {files} to {output_file}')
        if(len(files) == 0):
            return
    except :
        return
    video_generation_service.combine_videos(files,output_file)
    
    folder_tts = input_folder[len(default_values['processing_folder']):]
    folder,tts = folder_tts.split("/")[1:3]
    manga:Manga = database.get(Manga,Manga.folder==folder)[0]
    manga.status = update_status(manga.status,tts)
    database.save(manga)


def main():
     # Read default values from the configuration file
   

    parser = argparse.ArgumentParser(description="process images from inbox folder to processing folder")

    parser.add_argument("--input_folder", help="Input folder")
    parser.add_argument("--output_file", help="Folder path for processing")

    args = parser.parse_args()
    
    # Convert args namespace to a dictionary
    arguments = vars(args)
    merge_video_files([arguments[key] for key in ['input_folder','output_file']])

if __name__ == "__main__":
    main()
