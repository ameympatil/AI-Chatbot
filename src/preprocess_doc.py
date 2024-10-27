from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import TokenTextSplitter
from langchain_community.document_loaders import PyPDFLoader
import os

class PreprocessDoc:
    def __init__(self):
        self.embedding_function = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

    def pdf_loader(self, doc):
        loader = PyPDFLoader(doc)
        pages = loader.load_and_split()
        print("PDF Uploaded")
        return pages

    def create_chunks(self, text):
        text_splitter = TokenTextSplitter(chunk_size=512, chunk_overlap=128)
        chunks = text_splitter.split_documents(text)
        print("Chunks Created")
        return chunks

    def create_index(self, chunks, filename="default"):
        index = FAISS.from_documents(chunks, self.embedding_function)
        index.save_local(f"faiss_index/{filename}")
        print("Index Created")
        return index
    
    def get_index(self, filename):
        print(filename)
        if os.path.exists(f"faiss_index/{filename}"):
            print("yes")
            index = FAISS.load_local(f"faiss_index/{filename}", self.embedding_function, allow_dangerous_deserialization=True)
            return index
        else:
            raise FileNotFoundError(f"Index file not found: faiss_index/{filename}")

    def get_relevant_documents(self, query, index):
        docs = index.similarity_search(query, k=3)
        return docs
