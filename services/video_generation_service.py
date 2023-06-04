import argparse
import configparser
import json
from math import ceil
import os
import logging
import random
from typing import List
import logging.config
import os
from dtos.audio_metadata import AudioMetadata
from dtos.video_metadata import FileType, VideoMetadata
from moviepy.editor import *
import moviepy
from utils import fileutils
import copy

# Import the logging configuration from the logging_config module
logger = logging.getLogger(__name__)

# def generate_clip(src,file_type:FileType,sound_data:AudioMetadata,number_of_sounds):
#     if(file_type==FileType.IMAGE):
#         video_clip = ImageClip(src)
#     else:
#         video_clip = VideoClip(src)

#     sound_location = sound_data.position     
#     sound_clip = AudioFileClip(sound_data.src)
            
#     # Calculate the zoomed-in dimensions
#     zoomed_width = video_clip.w 
#     zoomed_height = video_clip.h/400

    
            
#     # Calculate the zoomed-in coordinates
#     zoomed_x = max(0, min(left - zoomed_width / 2, image_clip.w - zoomed_width))
#     zoomed_y = max(0, min(top - zoomed_height / 2, image_clip.h - zoomed_height))
    
#     x2 = min(zoomed_x+zoomed_width,image_clip.w )
#     y2 = min(zoomed_y+zoomed_height,image_clip.h )
#     # Apply zoom-in effect to the image clip for the current sound entry
    
#     zoomed_clip = image_clip.crop(x1=zoomed_x, y1=zoomed_y, x2=x2,y2=y2)
#     zoomed_clip = zoomed_clip.resize(height=720)
    
#     # Set audio for the final video and match the duration
#     final_clip = zoomed_clip.set_audio(sound_clip)
#     final_clip = final_clip.set_duration(sound_clip.duration)
#     return final_clip


def getOST():
    config = configparser.ConfigParser()
    config.read('config/app.ini')

    sound_values = config["SOUND"]
    ost_folder = sound_values["ost_folder"]
    audio_files = [fileutils.get_relative_path(ost_folder,file) for file in fileutils.get_files(ost_folder)]
    logger.debug(f'Audio files {audio_files}')
    if not audio_files:
        logger.error(f"No audio files found in {ost_folder} directory")
        return []
    random.shuffle(audio_files)
    return audio_files[:5]


def generate_base(src,file_type,page_part):
    if(file_type==FileType.IMAGE):
        video_clip = ImageClip(src)
    else:
        video_clip = VideoClip(src)

    return video_clip

def setPosition(panel_height,i,spped):
    return lambda t : (0,panel_height*i- (t*spped)) if (i!=2) else (0,max(0,panel_height*i- (t*spped)))

def generate_moving(image_clip:ImageClip, audio_clip:AudioClip,output_file):
    # image_clip = image_clip.scroll(y_speed=10)
    height=1080
    panel_height = ceil(height/3)
    duration = 20
    spped = (height-panel_height)/(duration - 1)
    image_clip = image_clip.resize(height=height)
    clips = [ image_clip.set_position(setPosition(panel_height,i,spped)).crop(0,panel_height*copy.deepcopy(i),image_clip.w,panel_height*copy.deepcopy(i)+panel_height).set_duration(duration) for i in range(0,3)]   
    if audio_clip is not None :
        clips[0]=clips[0].set_audio(audio_clip)
    final_clip = CompositeVideoClip(clips).set_duration(duration)
    final_clip = final_clip.resize(height=1080,width=1920)
    final_clip.write_videofile(output_file, codec='libx264', audio_codec='aac',fps=24)
    return final_clip

def combine_vertical(video_clips:List['VideoClip'],output_file):
    final_clip = concatenate_videoclips(video_clips,method='compose')
    if output_file.find('False') != -1:
        audio_clips = getOST()
        if len(audio_clips)!=0:
            audio_duration = final_clip.duration//len(audio_clips)
            audio_clips = [AudioFileClip(file).audio_loop(duration=audio_duration) for file in audio_clips]
            random.shuffle(audio_clips)
            audio_clip = concatenate_audioclips(audio_clips)
            final_clip = final_clip.set_audio(audio_clip)
    final_clip.write_videofile(output_file, codec='libx264', audio_codec='aac',fps=24)

def calculate_position(sound_data):
    
    data = []
    curr_t = 0
    for sound in sound_data :
        next_t = curr_t + sound['duration']
        data.append((curr_t,next_t,sound["x1"],sound["y1"]))
        curr_t = next_t

    print(data)
    def op(t):
        for elem in data:
            if t>=elem[0] and t<elem[1]:
                return (0,elem[3])
        return (0,data[len(data)-1][3])

    return op


def generate_video(video_metadata:VideoMetadata,output_file,tts):
    logger.debug(f"generate_video - {output_file}, tts=> {tts}")

    config = configparser.ConfigParser()
    config.read('config/app.ini')

    default_values = config["DEFAULT"]
    src = os.path.join(default_values['inbox_folder'],video_metadata.src)
    panels = video_metadata.panels
    
    if not tts :
        generate_moving(ImageClip(src),None,output_file)
        return 
    
    video_clips = []
    image_clip = ImageClip(src)
    duration = 0
    audio_clips = []

    for entry in panels:
        sounds = entry['sounds']
        panel = entry['panel']
        video_clip = image_clip.set_start(duration)
        start = duration
        for sound in sounds:
            try:
                audio_clip = AudioFileClip(sound['src'])
                audio_clip = audio_clip.set_start(duration)
                audio_clip_duration=audio_clip.duration+0.1
                audio_clips.append(audio_clip)
                duration+=audio_clip_duration
            except Exception as e:
                logger.error(e)
        if(start==duration):
            duration+=2
        y1 = max(0,min(panel[1],image_clip.h/2))
        y2 = min(max(panel[3],y1+image_clip.h/2),image_clip.h)
        x1 = 0
        x2 = image_clip.w
        video_clip = video_clip.crop(x1,y1,x2,y2)
        video_clip = video_clip.set_duration(duration-start)
        video_clip = video_clip.resize(width=1920)
        video_clips.append(video_clip)
    if len(video_clips) == 0 :
        return   
    final_video = CompositeVideoClip(video_clips).set_duration(duration)
    if len(audio_clips)>0:
        audio_clip = CompositeAudioClip(audio_clips).set_duration(duration)
        final_video = final_video.set_audio(audio_clip)
    final_video = final_video.resize(height=1080,width=1920)
    final_video.write_videofile(output_file, codec='libx264', audio_codec='aac',fps=24)

    

def generate_video_from_file(input_meatadata_file,output_file):
    logger.debug(f'{input_meatadata_file} {output_file}')
    vidoeMetadata = fileutils.read_file(input_meatadata_file)
    video_metadata:VideoMetadata = VideoMetadata(**json.loads(vidoeMetadata))
    generate_video(video_metadata=video_metadata,output_file=output_file,tts=input_meatadata_file.find('True')!=-1)

def combine_videos(input,output):
    # print(input)
    video_clips = [VideoFileClip(x) for x in input]
    combine_vertical(video_clips,output)
    
def main():

    parser = argparse.ArgumentParser(description="combine sources from input directory and generates a output vidoe file")

    parser.add_argument("--input_meatadata_file", help="Input directory")
    parser.add_argument("--output_file", help="Output Video")

    args = parser.parse_args()

    # Convert args namespace to a dictionary
    arguments = vars(args)

    generate_video_from_file(arguments['input_meatadata_file'],arguments['output_file'])
if __name__ == "__main__":
    main()

    # python -m services.video_generation_service --output_file resources/processed/black-clover-chapter-359-True.mp4  --input_meatadata_file resources/processing/black-clover-chapter-359/True/clovertcb_359_001-metadata.json 
