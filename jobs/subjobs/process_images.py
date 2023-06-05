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

def already_processed(folder,tts):
    manga_list = database.get(Manga,Manga.folder==folder)

    if(len(manga_list)==0):
        manga = Manga(folder=folder,status=0)
        database.save(manga)
        return False
    
    bit_0 = manga_list[0].status%2
    bit_1 = (manga_list[0].status//2)%2
    if tts:
        return bit_0 == 1
    else:
        return bit_1 == 1


def process_images(folders):
    inbox_folder,processing_folder,tts = folders
    folders = [folder for folder in fileutils.list_folders(inbox_folder) if not already_processed(folder,tts)]
    logger.debug(folders)
    
    fileutils.create_folders([fileutils.get_relative_path(processing_folder,folder) for folder in folders])
    logger.debug(f'folders to process => {len(folders)}')
    
    files = [(fileutils.get_relative_path(folder,file)) for folder in folders for file in fileutils.get_files(fileutils.get_relative_path(inbox_folder,folder))]
    logger.info(f'files to process => {len(files)}')
    i=0
    for file in files:
        i+=1
        logger.info(f'*********** generating clips -> progress {i}/{len(files)} ***********')
        metadata_file = process_image_and_write_video_metadata({
            'input_image':file,
            'output_directory':processing_folder,
            'tts':tts
        })
        file_name = fileutils.get_tts_file_name(file,tts)

        output_file =  fileutils.get_relative_path(processing_folder,fileutils.change_extension(file_name,"mp4"))
        video_generation_service.generate_video_from_file(input_meatadata_file=metadata_file,output_file=output_file)

    

def main():
     # Read default values from the configuration file
    config = configparser.ConfigParser()
    config.read('config/app.ini')

    default_values = config["DEFAULT"]

    parser = argparse.ArgumentParser(description="process images from inbox folder to processing folder")

    parser.add_argument("--inbox_folder", default=default_values.get("inbox_folder"), help="Folder path for inbox")
    parser.add_argument("--processing_folder", default=default_values.get("processing_folder"), help="Folder path for processing")
    parser.add_argument("--tts_enabled", default=default_values.getboolean("tts_enabled"), help="Enable text-to-speech")

    args = parser.parse_args()
    
    # Convert args namespace to a dictionary
    arguments = vars(args)

    if(arguments['tts_enabled'] == 'True'):
        arguments['tts_enabled'] = True
    if(arguments['tts_enabled'] == 'False'):
        arguments['tts_enabled'] = False

    process_images([arguments[key] for key in ['inbox_folder','processing_folder','tts_enabled']])

if __name__ == "__main__":
    main()
