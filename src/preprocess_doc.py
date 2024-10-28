from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import TokenTextSplitter
from langchain_community.document_loaders import PyPDFLoader
import os


class PreprocessDoc:
    """
    A class for preprocessing documents, including loading PDFs, creating chunks,
    creating and retrieving indexes, and searching for relevant documents.
    """

    def __init__(self):
        """
        Initializes the PreprocessDoc class with a GoogleGenerativeAIEmbeddings instance.
        """
        self.embedding_function = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001"
        )

    def pdf_loader(self, doc):
        """
        Loads and splits a PDF document into pages.

        Args:
        - doc (str): The path to the PDF document.

        Returns:
        - list: A list of pages extracted from the PDF.
        """
        try:
            loader = PyPDFLoader(doc)
            pages = loader.load_and_split()
            print("PDF Uploaded")
            return pages
        except Exception as e:
            print(f"Error loading PDF: {e}")
            return []

    def create_chunks(self, text):
        """
        Splits a given text into chunks based on a specified size and overlap.

        Args:
        - text (str): The text to be split into chunks.

        Returns:
        - list: A list of chunks created from the input text.
        """
        try:
            text_splitter = TokenTextSplitter(chunk_size=512, chunk_overlap=128)
            chunks = text_splitter.split_documents(text)
            print("Chunks Created")
            return chunks
        except Exception as e:
            print(f"Error creating chunks: {e}")
            return []

    def create_index(self, chunks, filename="default"):
        """
        Creates a FAISS index from a list of chunks and saves it locally.

        Args:
        - chunks (list): A list of chunks to be indexed.
        - filename (str, optional): The filename for the index. Defaults to "default".

        Returns:
        - FAISS: The created FAISS index.
        """
        try:
            index = FAISS.from_documents(chunks, self.embedding_function)
            index.save_local(f"faiss_index/{filename}")
            print("Index Created")
            return index
        except Exception as e:
            print(f"Error creating index: {e}")
            return None

    def get_index(self, filename):
        """
        Loads a locally saved FAISS index by its filename.

        Args:
        - filename (str): The filename of the index to be loaded.

        Returns:
        - FAISS: The loaded FAISS index.
        """
        try:
            if os.path.exists(f"faiss_index/{filename}"):
                index = FAISS.load_local(
                    f"faiss_index/{filename}",
                    self.embedding_function,
                    allow_dangerous_deserialization=True,
                )
                return index
            else:
                raise FileNotFoundError(f"Index file not found: faiss_index/{filename}")
        except Exception as e:
            print(f"Error loading index: {e}")
            return None

    def get_relevant_documents(self, query, index):
        """
        Performs a similarity search on the index to find relevant documents.

        Args:
        - query (str): The query to search for.
        - index (FAISS): The FAISS index to search in.

        Returns:
        - list: A list of relevant documents based on the query.
        """
        try:
            docs = index.similarity_search(query, k=3)
            return docs
        except Exception as e:
            print(f"Error searching for documents: {e}")
            return []
