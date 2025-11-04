import fitz
def extract_text_from_pdf_optimised(file_path : str) -> str:
    doc=fitz.open(file_path)
    text=""
    for page in doc:
        pagetext = page.get_text("text")
        text += str(pagetext)
    doc.close()
    return text
    
    
def extract_text_from_large_pdf(file_path: str) -> str:
    texts = []
    doc= fitz.open(file_path)
    for page in doc:
        texts.append(page.get_text("text"))
        
    return "\n".join(texts)