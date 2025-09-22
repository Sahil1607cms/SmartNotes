from langchain.text_splitter import RecursiveCharacterTextSplitter

def chunk_text(text):
    splitter=RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=10
    )

    return splitter.split_text(text)
