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

#print(formatted_lyrics.strip())


# # Let’s also save the transcription to a text file so we can use it later!"
with open("transcription.txt", "w", encoding="utf-8") as file:
    file.write(formatted_lyrics.strip())

print("Transcription saved to transcription.txt")


# transcript_data = formatted_lyrics.strip()

# # Save it into a Python file
# with open("transcript_data.py", "w", encoding="utf-8") as f:
#     f.write(f"transcript_text = '''{transcript_data}'''")
