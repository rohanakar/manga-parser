import moviepy.editor as mpy
import moviepy.video.fx.all as vfx
from .fileutils import open_file as open_metadata
import json

def generate_video(metadata_file):
    metadata = open_metadata(metadata_file)
    metadata = json.loads(metadata)


from moviepy.editor import *

def generate_video(metadata):
    image_path = metadata['image']
    sounds_data = metadata['sounds']
    output_path = metadata['output']
    
    image_clip = ImageClip(image_path)
    
    # Resize the image to fit YouTube video standards (1280x720)
    image_clip = image_clip.resize(height=720)
    
    # Check if there are any sound entries in the metadata
    if len(sounds_data) > 0:
        # Create a list to store individual audio clips
        audio_clips = []
        max_audio_duration = 0
        
        for sound_data in sounds_data:
            sound_location = sound_data['location']
            top = sound_data['top']
            left = sound_data['left']
            
            sound_clip = AudioFileClip(sound_location)
            
            # Calculate zoom-in scale based on the top and left coordinates
            zoom_scale = 2.0  # Adjust this value as per your requirement
            
            # Calculate the zoomed-in dimensions
            zoomed_width = image_clip.w / zoom_scale
            zoomed_height = image_clip.h / zoom_scale
            
            # Calculate the zoomed-in coordinates
            zoomed_x = max(0, min(left - zoomed_width / 2, image_clip.w - zoomed_width))
            zoomed_y = max(0, min(top - zoomed_height / 2, image_clip.h - zoomed_height))
            
            # Apply zoom-in effect to the image clip for the current sound entry
            zoomed_clip = image_clip.crop(x1=zoomed_x, y1=zoomed_y, x2=zoomed_x+zoomed_width, y2=zoomed_y+zoomed_height)
            zoomed_clip = zoomed_clip.resize(height=720)
            
            # Set audio for the zoomed clip
            zoomed_clip = zoomed_clip.set_audio(sound_clip)
            
            # Set the duration for the zoomed clip based on audio clip's duration
            zoomed_clip = zoomed_clip.set_duration(sound_clip.duration)
            
            # Add the zoomed clip to the list of audio clips
            audio_clips.append(zoomed_clip.audio)
            
            # Update the maximum audio duration
            max_audio_duration = max(max_audio_duration, sound_clip.duration)
        
        # Check if there are any audio clips
        if audio_clips:
            # Create a composite audio clip from the individual audio clips
            final_audio = concatenate_audioclips(audio_clips)
        else:
            # If there are no audio clips, create a silent audio clip
            final_audio = AudioFileClip('', duration=max_audio_duration)
        
        # Set the audio for the final video
        final_clip = image_clip.set_audio(final_audio)
        
        # Set the duration for the final video based on the maximum audio duration
        final_clip = final_clip.set_duration(max_audio_duration)
    else:
        # If there are no sound entries, use only the image clip
        final_clip = image_clip
    
    # Write the final video to the output directory
    final_clip.write_videofile(output_path, codec='libx264', audio_codec='aac')

# Example usage with the provided metadata
metadata = {
    "image": "/Users/rischaud/opensrc/manga-parser/resources/inbox/one piece/a.jpeg",
    "sounds": [
        {
            "location": "/Users/rischaud/opensrc/manga-parser/resources
