from langchain_community.vectorstores import FAISS

def store_embeddings(chunks,embeddings,source_id):
    path=f"faiss_index/{source_id}"
    vectorstore = FAISS.from_texts(chunks,embeddings)
    vectorstore.save_local(path)
    return vectorstore

def load_embeddings(embeddings,source_id):
    path=f"faiss_index/{source_id}"
    vectorstore = FAISS.load_local(path,embeddings, allow_dangerous_deserialization=True)
    return vectorstore

def retrieve_relevant_docs(embeddings,source_id,query,top_k=3):
    vectorstore=load_embeddings(embeddings,source_id)
    docs = vectorstore.similarity_search(query,k=top_k)
    return docs