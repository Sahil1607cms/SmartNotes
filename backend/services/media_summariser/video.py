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

#print(formatted_lyrics.strip())


# # Let’s also save the transcription to a text file so we can use it later!"
# with open("transcription.txt", "w", encoding="utf-8") as file:
#     file.write(formatted_lyrics.strip())

# print("Transcription saved to transcription.txt")


#summarizing 
##############################################
model_id =  "meta-llama/Llama-3.2-3B-Instruct"
DEFAULT_MODEL = "meta-llama/Llama-3.2-1B-Instruct"


model = AutoModelForCausalLM.from_pretrained(
    DEFAULT_MODEL,
    dtype=torch.bfloat16,
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
    {"role": "user", "content": f'''{formatted_lyrics.strip()}'''},
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


# from transformers import pipeline
# from langchain_huggingface import HuggingFacePipeline
# from langchain.prompts import PromptTemplate
# from transformers.utils.logging import set_verbosity_error

# set_verbosity_error()

# summarization_pipeline = pipeline("summarization", model="facebook/bart-large-cnn")
# summarizer = HuggingFacePipeline(pipeline=summarization_pipeline)

# refinement_pipeline = pipeline("summarization", model="facebook/bart-large")
# refiner = HuggingFacePipeline(pipeline=refinement_pipeline)

# qa_pipeline = pipeline("question-answering", model="deepset/roberta-base-squad2")

# summary_template = PromptTemplate.from_template("Summarize the following text in a :\n\n{text}")

# summarization_chain = summary_template | summarizer | refiner

# text_to_summarize = formatted_lyrics.strip()
# #length = input("\nEnter the length (short/medium/long): ")

# summary = summarization_chain.invoke({"text": text_to_summarize})

# print("\n🔹 **Generated Summary:**")
# print(summary)

# while True:
#     question = input("\nAsk a question about the summary (or type 'exit' to stop):\n")
#     if question.lower() == "exit":
#         break

#     qa_result = qa_pipeline(question=question, context=summary)

#     print("\n🔹 **Answer:**")
#     print(qa_result["answer"])
#    

    