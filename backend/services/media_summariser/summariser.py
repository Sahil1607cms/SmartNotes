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


model_id =  "meta-llama/Llama-3.2-3B-Instruct"
DEFAULT_MODEL = "meta-llama/Llama-3.2-1B-Instruct"


model = AutoModelForCausalLM.from_pretrained(
    DEFAULT_MODEL,
    torch_dtype=torch.bfloat16,
    use_safetensors=True,
    device_map=device,
    load_in_4bit=True, 
)

tokenizer = AutoTokenizer.from_pretrained(DEFAULT_MODEL, use_safetensors=True)
tokenizer.pad_token_id = tokenizer.eos_token_id

conversation = [
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

prompt = tokenizer.apply_chat_template(conversation, tokenize=False)
inputs = tokenizer(prompt, return_tensors="pt").to(device)
# print(prompt)

with torch.no_grad():
    output = model.generate(
        **inputs,
        do_sample=True,
        max_new_tokens=1000
    )

processed_text = tokenizer.decode(output[0][len(inputs.input_ids[0]):], skip_special_tokens=True)

print(processed_text)