import asyncio
from langchain_google_genai import GoogleGenerativeAIEmbeddings 
from dotenv import load_dotenv
import os

load_dotenv()

google_api_key=os.environ["GOOGLE_API_KEY"]

embedder = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

async def generate_embeddings_async(chunks):
    loop = asyncio.get_event_loop() 
    tasks=[]
    for chunk in chunks:
        task = loop.run_in_executor(None, embedder.embed_query, chunk)
        tasks.append(task)
    embeddings = await asyncio.gather(*tasks)
    return embeddings