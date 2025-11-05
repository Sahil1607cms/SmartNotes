from fastapi import APIRouter, UploadFile, Form
from services.rag_service import rag_chat
import asyncio
import os

router = APIRouter()

@router.post("/chat")
async def chat_endpoint(query: str = Form(...), pdf: UploadFile = None, text: str = Form(None)):
    pdf_path = None
    if pdf:
        os.makedirs("temp", exist_ok=True)
        pdf_path = f"temp/{pdf.filename}"
        with open(pdf_path, "wb") as f:
            f.write(await pdf.read())
    response = await rag_chat(query=query, text_data=text, pdf_path=pdf_path)
    return {"response": response}

# git pull --rebase