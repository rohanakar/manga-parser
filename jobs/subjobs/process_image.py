import argparse
import configparser
import json
import logging

import logging.config
import random
from dtos.audio_metadata import AudioMetadata, Rectangle
from dtos.video_metadata import FileType, VideoMetadata

from services import ocr_service, tts_service, video_generation_service
from utils import fileutils

# Import the logging configuration from the logging_config module
logger = logging.getLogger(__name__)

def getOST():
    config = configparser.ConfigParser()
    config.read('config/app.ini')

    sound_values = config["SOUND"]
    ost_folder = sound_values["ost_folder"]
    audio_files = [fileutils.get_relative_path(ost_folder,file) for file in fileutils.get_files(ost_folder)]
    
    logger.debug(f'Audio files {audio_files}')
    if not audio_files:
        logger.error(f"No audio files found in {ost_folder} directory")
        return ''
    return random.choice(audio_files)

def process_image_and_write_video_metadata(arguments):
    input_image,output_directory,tts = arguments.values()

    logger.debug(f' processing {input_image} ')
    input_file_name = input_image
    file_name = fileutils.get_tts_file_name(input_file_name,tts)
    output_file_name= file_name +f"-metadata.json"
    
    fileutils.create_folders([fileutils.get_relative_path(output_directory,'/'.join([ x for x in file_name.split("/")[:-1]]))])
    output_file = fileutils.get_relative_path(output_directory,output_file_name)
    
    logger.debug(f' writing metadata to  {output_file} with tts => {tts}')
    if fileutils.exist(output_file):
        return output_file
    
    if not tts:
        audioFile = getOST()
        audio_metadata = AudioMetadata(audioFile,Rectangle(0,0,0,0))
        video_metadata = VideoMetadata(input_image,FileType.IMAGE,[{'sounds':[audio_metadata],'panel':[0,0,2000,2000]}])
        logger.debug(video_metadata)
        video_metadata = json.dumps(video_metadata,default=lambda o: o.__dict__,  indent=4)
        fileutils.writeToFile(output_file,video_metadata,'w')
        return output_file
    
    ocr_data = ocr_service.performOCR(input_image,details=True)
    logger.debug(f' ocr_data => {ocr_data}')
    count = 0
    audio_metadata = []
    for panel_data in ocr_data:
        sound_data = panel_data['sound_data']
        audio_metadata_unit=[]
        for sound in sound_data:
            i =0
            lineText = sound['LineText']
            del sound['LineText']
            while(i<len(lineText)):
                line = lineText[i:i+90]
                output_sound_file_name= file_name +f"-tts-{tts}-{count}.mp3"
                output_sound_file = fileutils.get_relative_path(output_directory,output_sound_file_name)
                tts_service.performTTS(line,output_sound_file)
                count+=1
                i+=90
                audio_metadata_unit.append({'src':output_sound_file,'position':sound})            
        audio_metadata.append({'sounds':audio_metadata_unit,'panel':panel_data['panel']})
            
    video_metadata = VideoMetadata(input_image,FileType.IMAGE,audio_metadata)
    video_metadata = json.dumps(video_metadata,default=lambda o: o.__dict__,  indent=4)
    fileutils.writeToFile(output_file,video_metadata,'w')
    return output_file

def main():

    parser = argparse.ArgumentParser(description="process image to output directory")
    config = configparser.ConfigParser()
    config.read('config/app.ini')

    default_values = config["DEFAULT"]
    parser.add_argument("--input_image",help="Input image")
    parser.add_argument("--output_directory", help="output directory")
    parser.add_argument("--tts_enabled", default=default_values.getboolean("tts_enabled"), help="Enable text-to-speech")

    args = parser.parse_args()

    # Convert args namespace to a dictionary
    arguments = vars(args)
    if(arguments['tts_enabled'] == 'True'):
        arguments['tts_enabled'] = True
    if(arguments['tts_enabled'] == 'False'):
        arguments['tts_enabled'] = False
    process_image_and_write_video_metadata(arguments)
    
    
if __name__ == "__main__":
    main()


# python -m jobs.subjobs.process_image --input_image spy-x-family-chapter-78-/spyfam_78_11.jpg --tts_enabled True --output_directory test
