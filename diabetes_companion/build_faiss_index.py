
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS


file_path = "knowledge.md"
loader = TextLoader(file_path)
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=50)
docs = loader.load_and_split(text_splitter=text_splitter)

# Generate embeddings
embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en", model_kwargs={'device': 'cpu'})
vector_db = FAISS.from_documents(docs, embeddings)

vector_db.save_local("faiss_index")

