
from transformers import pipeline,AutoModelForCausalLM, AutoTokenizer
import torch
from IPython.display import  clear_output

from dotenv import load_dotenv, find_dotenv
import os


from faster_whisper import WhisperModel, BatchedInferencePipeline
import torch
device = 'cuda' if torch.cuda.is_available() else 'cpu' 
load_dotenv()
HF_TOKEN=os.environ.get("HF_TOKEN")
if not HF_TOKEN:
    raise ValueError("Missing HF_TOKEN in .env")




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

# # for l in transcript:
# #     print(l)


# # formatted_lyrics = ""
# # for segment in segments:
# #     for line in segment['chunks']:       
# #        text = line["text"]
# #        ts = line["timestamp"]
# #        formatted_lyrics += f"{ts}-->{text}\n"

# # #print(formatted_lyrics.strip())


# # # # Let’s also save the transcription to a text file so we can use it later!"
# # with open("transcription.txt", "w", encoding="utf-8") as file:
# #      file.write(formatted_lyrics.strip())

# # print("Transcription saved to transcription.txt")


# #     #summarizing 
# # ##############################################
# print("Starting the summarisation process ....")
# model_id =  "meta-llama/Llama-3.2-3B-Instruct"
# DEFAULT_MODEL = "meta-llama/Llama-3.2-1B-Instruct"


# model = AutoModelForCausalLM.from_pretrained(
#     DEFAULT_MODEL,
#     dtype=torch.bfloat16,
#     use_safetensors=True,
#     device_map=device,
#     #load_in_4bit=True, 
# )

# tokenizer = AutoTokenizer.from_pretrained(DEFAULT_MODEL, use_safetensors=True)
# tokenizer.pad_token_id = tokenizer.eos_token_id

# conversation = [
#     {"role": "system", "content": '''You are an expert at summarizing transcripts. I will provide you with a transcript of a video or audio. Your task is to generate a summary in bullet points that:

# Covers all important aspects of the transcript (no skipping meaningful content).

# Is shorter than the transcript itself (no copy-pasting or paraphrasing everything).

# Clearly states the main idea and the key takeaways.

# Is written in simple, natural language that’s easy to understand.

# Does not include filler words, timestamps, or unnecessary repetition.

# Format:

# Start with a one-line overview of the video/meeting.

# Then provide bullet points with the key takeaways.

# If any data, reference, or example is in the transcript, include it concisely in the bullets.'''},
#     {"role": "user", "content": f'''{transcript}'''},
# ]

# prompt = tokenizer.apply_chat_template(conversation, tokenize=False)
# inputs = tokenizer(prompt, return_tensors="pt").to(device)
# # print(prompt)

# with torch.no_grad():
#     output = model.generate(
#         **inputs,
#         do_sample=True,
#         max_new_tokens=1000
#     )

# processed_text = tokenizer.decode(output[0][len(inputs.input_ids[0]):], skip_special_tokens=True)

# print(processed_text)





