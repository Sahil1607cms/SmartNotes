import asyncio
from utils.text_chunking import chunk_text
from utils.embeddings import generate_embeddings_async
from utils.vector_db import store_embeddings,retrieve_relevant_docs
from utils.pdf_loader import extract_text_from_pdf_optimised,extract_text_from_large_pdf
from langchain_groq import ChatGroq

async def rag_chat(query, text_data=None, pdf_path=None, source_id=None):
    if pdf_path:
        text_data= extract_text_from_pdf_optimised(pdf_path)
    if not text_data or len(text_data.strip())==0:
        return "No content provided"

    chunks= chunk_text(text_data)
    embeddings = generate_embeddings_async(chunks)
    store_embeddings(chunks,embeddings,source_id)
    docs = retrieve_relevant_docs(embeddings,source_id,query)
    context = " ".join([d.page_content for d in docs])
    llm = ChatGroq(model="llama3-70b-8192")

    prompt = f"""
    Use the context below to answer the question.

    Context (from source {source_id}):
    {context}

    Question: {query}
    """

    response = await llm.ainvoke(prompt)
    return response.content