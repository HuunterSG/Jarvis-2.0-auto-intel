import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

class JarvisMemory:
    """
    Manages the RAG system by indexing Axalta technical data sheets.
    """
    def __init__(self):
        # Use OpenAI standard embeddings for professional-grade semantic search
        self.embeddings = OpenAIEmbeddings()
        self.vector_store = None

    def process_manuals(self, data_path: str = "data/"):
        """Reads Axalta PDFs and initializes the FAISS vector database."""
        documents = []
        if not os.path.exists(data_path):
            os.makedirs(data_path)
            
        for file in os.listdir(data_path):
            if file.endswith(".pdf"):
                loader = PyPDFLoader(os.path.join(data_path, file))
                documents.extend(loader.load())
        
        if not documents:
            print("Warning: No technical PDFs found in /data.")
            return

        # Split technical text into overlapping chunks to maintain context
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=150)
        chunks = text_splitter.split_documents(documents)
        
        # Build searchable database
        self.vector_store = FAISS.from_documents(chunks, self.embeddings)
        print(f"Memory synced: {len(chunks)} technical segments loaded from Axalta TDS.")

    def search_manuals(self, query: str):
        """Finds the most relevant technical data for a given query."""
        if not self.vector_store:
            return ""
        # Retrieve the top 3 relevant context chunks
        results = self.vector_store.similarity_search(query, k=3)
        return "\n".join([res.page_content for res in results])