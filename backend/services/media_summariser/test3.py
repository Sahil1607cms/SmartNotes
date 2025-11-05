from transformers import pipeline,AutoModelForCausalLM, AutoTokenizer
import torch
from IPython.display import  clear_output

from dotenv import load_dotenv, find_dotenv
import os
load_dotenv()
HF_TOKEN=os.environ.get("HF_TOKEN")
if not HF_TOKEN:
    raise ValueError("Missing HF_TOKEN in .env")
#os.environ["HF_TOKEN"] = "your_hf_token"

# model = AutoModelForCausalLM.from_pretrained(
#     "meta-llama/Llama-3.2-3B-Instruct",
#     token=os.environ["HF_TOKEN"],
#     device_map="auto"
# )


device = 'cuda' if torch.cuda.is_available() else 'cpu' 

import subprocess

def convert_mp4_to_mp3(input_file, output_file):
    """Convert an MP4 file to MP3 using ffmpeg."""
    try:
        command = [
            "ffmpeg",
            "-i", input_file,    # Input file
            "-vn",               # No video
            "-acodec", "libmp3lame",  # MP3 codec
            "-b:a", "192k",      # Audio bitrate
            output_file          # Output file
        ]
        subprocess.run(command, check=True)
        print(f"Conversion successful: {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error during conversion: {e}")

# Example usage
#convert_mp4_to_mp3("2025-03-21 10-15-55.mp4", "meeting.mp3")


pipe  = pipeline("automatic-speech-recognition",
                    "openai/whisper-small", 
                    chunk_length_s=30,
                    stride_length_s=5,
                    return_timestamps=True,
                    device=device, 
                    generate_kwargs = {"language": 'english', "task": "transcribe"}) 


transcription = pipe("sho.mp3" )
#Once the transcription is complete, we’ll format the text with timestamps for better readability.
formatted_lyrics = ""
for line in transcription['chunks']:
    text = line["text"]
    ts = line["timestamp"]
    formatted_lyrics += f"{ts}-->{text}\n"


import torch
from transformers import pipeline

model_id = "meta-llama/Llama-3.2-1B-Instruct"
pipe = pipeline(
    "text-generation",
    model=model_id,
    torch_dtype=torch.bfloat16,
    device_map="auto",
)
messages = [
    {"role": "system", "content": "You are a pirate chatbot who always responds in pirate speak!"},
    {"role": "user", "content": "Who are you?"},
]

con = [
    {"role": "system", "content": '''You are an expert at summarizing transcripts. I will provide you with a transcript of a video or audio. Your task is to generate a summary in bullet points that:

Covers all important aspects of the transcript (no skipping meaningful content).

Is shorter than the transcript itself (no copy-pasting or paraphrasing everything).

Clearly states the main idea and the key takeaways.

Is written in simple, natural language that’s easy to understand.

Does not include filler words, timestamps, or unnecessary repetition.

Format:

Start with a one-line overview of the video/meeting.

Then provide bullet points with the key takeaways.

If any data, reference, or example is in the transcript, include it concisely in the bullets.'''},
    {"role": "user", "content": f'''{formatted_lyrics.strip()}'''},
]
outputs = pipe(
    con,
    max_new_tokens=500,
)
print(outputs[0]["generated_text"][-1])
