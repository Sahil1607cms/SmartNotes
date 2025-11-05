from transformers import pipeline,AutoModelForCausalLM, AutoTokenizer
import torch
from IPython.display import  clear_output


device = 'cuda' if torch.cuda.is_available() else 'cpu' 

import subprocess

def convert_mp4_to_mp3(input_file, output_file, speed=1.25):
    """Convert an MP4 file to MP3 using ffmpeg."""
    try:
        command = [
            "ffmpeg",
            "-i", input_file,    # Input file
            "-vn",               # No video
            "-filter:a", f"atempo={speed}", #spped up the audio 
            "-acodec", "libmp3lame",  # MP3 codec
            "-b:a", "192k",      # Audio bitrate
            output_file          # Output file
        ]
        subprocess.run(command, check=True)
        print(f"Conversion successful: {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error during conversion: {e}")

# Example usage
#convert_mp4_to_mp3("elon.mp4", "sho.mp3")

#print("Conversion succesfull")