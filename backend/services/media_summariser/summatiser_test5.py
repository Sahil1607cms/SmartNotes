from transformers import pipeline,AutoModelForCausalLM, AutoTokenizer
import torch
from IPython.display import  clear_output

from dotenv import load_dotenv, find_dotenv
import os
load_dotenv()
HF_TOKEN=os.environ.get("HF_TOKEN")
if not HF_TOKEN:
    raise ValueError("Missing HF_TOKEN in .env")

device = 'cuda' if torch.cuda.is_available() else 'cpu' 

with open("../video_summary/transcription.txt", "r", encoding="utf-8") as f:
    transcript_text = f.read()


model_id = "meta-llama/Llama-3.2-1B-Instruct"
pipe = pipeline(
    "text-generation",
    model=model_id,
    dtype=torch.bfloat16,
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
    {"role": "user", "content": f'''{transcript_text.strip()}'''},
]
outputs = pipe(
    con,
    max_new_tokens=500,
)
print(outputs[0]["generated_text"][-1])
