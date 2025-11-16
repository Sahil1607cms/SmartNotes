from groqs import summarize_transcript  
import os
from transformers import pipeline,AutoModelForCausalLM, AutoTokenizer
import torch
from IPython.display import  clear_output

from dotenv import load_dotenv, find_dotenv
import os
import gc, torch, psutil, os
from faster_whisper import WhisperModel, BatchedInferencePipeline
from video_to_audio import convert_mp4_to_mp3  
env_path = "/full/path/to/.env"
load_dotenv(env_path)   



gc.collect()

if torch.cuda.is_available():
    torch.cuda.empty_cache()



import torch
device = 'cuda' if torch.cuda.is_available() else 'cpu' 
load_dotenv()
HF_TOKEN=os.environ.get("HF_TOKEN")
if not HF_TOKEN:
    raise ValueError("Missing HF_TOKEN in .env")

#video to audio part 


convert_mp4_to_mp3("elon.mp4", "sho.mp3")

#audio to transcript 

#print(device)
model = WhisperModel("small", device, compute_type="float16")
batched_model = BatchedInferencePipeline(model=model)
segments, info = batched_model.transcribe("sho.mp3", batch_size=8, word_timestamps=True)
#segments = list(segments) 

#print(segments)
transcript=[]
with open("transcription.txt", "w", encoding="utf-8") as file:
    for segment in segments:
       #print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))
       line = "[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text)
       file.write(line+"\n")
       transcript.append(line)



print("\nThe text file has create succesfully\n")

#summarising part begins
from prompt import my_custom_prompt

my_transcript = transcript

# Call the summarizer
summary = summarize_transcript(
    transcript=my_transcript,  # <-- your transcript goes here
    prompt=my_custom_prompt,    # <-- your prompt goes here (optional)
    style="general",            # or "bullet_points", "executive", etc.
    model="llama-3.3-70b-versatile",     # optional, defaults to this
    api_key=os.getenv("GROQ_API_KEY")  # <-- pass it here
)

print("=== Summary ===")
print(summary)


# free Whisper model
del model
gc.collect()

if torch.cuda.is_available():
    torch.cuda.empty_cache()