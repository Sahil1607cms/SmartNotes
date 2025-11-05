from langchain_text_splitters import RecursiveCharacterTextSplitter

text_splitter=RecursiveCharacterTextSplitter(
    chunk_size=1500,
    chunk_overlap=200,
    separators=["\n\n", "\n", ".", " ", ""],
)
def chunk_text(text):
    return text_splitter.split_text(text)

    
