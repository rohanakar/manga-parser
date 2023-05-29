from moviepy.editor import *

from .fileutils import open_file as open_metadata
import json
import os
import shutil

def generate_clip(image_clip,sound_data):
    sound_location = sound_data['location']
    top = sound_data['top']
    left = sound_data['left']        
    sound_clip = AudioFileClip(sound_location)
    zoom_scale = 1.5 # Adjust this value as per your requirement
            
    # Calculate the zoomed-in dimensions
    zoomed_width = image_clip.w 
    zoomed_height = image_clip.h / zoom_scale
            
    # Calculate the zoomed-in coordinates
    zoomed_x = max(0, min(left - zoomed_width / 2, image_clip.w - zoomed_width))
    zoomed_y = max(0, min(top - zoomed_height / 2, image_clip.h - zoomed_height))
    
    x2 = min(zoomed_x+zoomed_width,image_clip.w )
    y2 = min(zoomed_y+zoomed_height,image_clip.h )
    # Apply zoom-in effect to the image clip for the current sound entry
    
    zoomed_clip = image_clip.crop(x1=zoomed_x, y1=zoomed_y, x2=x2,y2=y2)
    zoomed_clip = zoomed_clip.resize(height=720)
    
    # Set audio for the final video and match the duration
    final_clip = zoomed_clip.set_audio(sound_clip)
    final_clip = final_clip.set_duration(sound_clip.duration)
    return final_clip

def generate_video(metadata_file):
    metadata = open_metadata(metadata_file)
    metadata = json.loads(metadata)
    image_path = metadata['image']
    sounds_data = metadata['sounds']
    output_path = metadata['output']

    videos = []
    for sound_data in sounds_data:
        try:
            vido_clip = generate_clip(ImageClip(image_path),sound_data)
            videos.append(vido_clip)
        except Exception as e:
            print(e)
        

    final_video = concatenate_videoclips(videos,method='compose')

    # image_clip = ImageClip(image_path)
    
    # # Resize the image to fit YouTube video standards (1280x720)
    # image_clip = image_clip.resize(height=720)
    
    # # Check if there are any sound entries in the metadata
    # if len(sounds_data) > 0:
    #     # Create a list to store individual audio clips
    #     audio_clips = []
    #     max_audio_duration = 0

    #     for sound_data in sounds_data:
    #         sound_location = sound_data['location']
    #         top = sound_data['top']
    #         left = sound_data['left']
            
    #         sound_clip = AudioFileClip(sound_location)
            

    #         zoomed_clip = image_clip.set_audio(sound_clip)
            
    #         # Set the duration for the zoomed clip based on audio clip's duration
    #         zoomed_clip = zoomed_clip.set_duration(sound_clip.duration)
    #         # Add the zoomed clip to the list of audio clips
    #         audio_clips.append(zoomed_clip.audio)
    #         max_audio_duration = max_audio_duration+ sound_clip.duration

    #     # Check if there are any audio clips
    #     if audio_clips:
    #         # Create a composite audio clip from the individual audio clips
    #         final_audio = concatenate_audioclips(audio_clips)
    #     else:
    #         # If there are no audio clips, create a silent audio clip
    #         final_audio = AudioFileClip('', duration=image_clip.duration)
        
    #     # Set the audio for the final video
    #     final_clip = image_clip.set_audio(final_audio)

    #     # Set the duration for the final video based on the maximum audio duration
    #     final_clip = final_clip.set_duration(max_audio_duration)
    # else:
    #     # If there are no sound entries, use only the image clip
    #     final_clip = image_clip
    
    # # final_clip = final_clip.set_position(position)
    # # Write the final video to the output directory
    final_video.write_videofile(output_path, codec='libx264', audio_codec='aac',fps=24)

def delete_folder(path):
    # Delete all files and sub-folders
    for root, dirs, files in os.walk(path, topdown=False):
        for file in files:
            file_path = os.path.join(root, file)
            os.remove(file_path)
        for dir in dirs:
            dir_path = os.path.join(root, dir)
            shutil.rmtree(dir_path)

    # Delete the parent folder itself
    shutil.rmtree(path)


def combine_video_and_clean_up():
    directory='/Users/rischaud/opensrc/manga-parser/resources/processing'
    directory_list = get_directory_structure(directory)
    # print(response)
    for dir in directory_list:
        videos = []
        output_path = dir[0]
        input_path = dir[0].replace('processed','processing')
        videos_path = dir[1]
        output_file=output_path+".mp4"
        # print(f'preparing to write {output_file}')
        for video_path in videos_path:
            video_clip = VideoFileClip(video_path)
            videos.append(video_clip)
        final_video = concatenate_videoclips(videos,method='compose')
        final_video.write_videofile(output_file, codec='libx264', audio_codec='aac',fps=24)
        print(f'removing procesing folder {input_path}')
        delete_folder(input_path)

def get_directory_structure(root_dir):
    directory_list = []

    for manga_folder in os.listdir(root_dir):
        folder = os.path.join(root_dir, manga_folder)
        if(manga_folder.startswith('.')):
            continue
        files=[]       

        for file in os.listdir(folder):
            file_path = os.path.join(folder, file)
            if os.path.isfile(file_path) and file_path.endswith('.mp4'):
                files.append(file_path)
            
        directory_list.append((folder.replace('processing','processed'),sorted(files)))
        
    # for root, dirs, files in os.walk(root_dir):
    #     # Skip the root directory itself
    #     if root == root_dir:
    #         continue
        
    #     # Extract the relative path
    #     rel_path = os.path.relpath(root, root_dir)
        
    #     # Collect files within the current directory
    #     file_list = [os.path.join(rel_path, file) for file in files]
        
    #     # Append to the directory list
    #     print(rel_path)
    #     directory_list.append((rel_path, file_list))
    
    return directory_list

