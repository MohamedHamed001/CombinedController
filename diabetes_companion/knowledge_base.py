from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

def get_retriever():
    embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en", model_kwargs={'device': 'cpu'})
    vector_db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
    return vector_db.as_retriever()
