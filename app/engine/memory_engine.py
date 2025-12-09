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
        self.retriever = None

    def process_manuals(self, data_path: str = "data/"):
        """Reads Axalta PDFs and initializes the FAISS vector database."""
        documents = []
        if not os.path.exists(data_path):
            os.makedirs(data_path)
            
        # 1. Carga de Documentos
        for file in os.listdir(data_path):
            if file.endswith(".pdf"):
                try:
                    loader = PyPDFLoader(os.path.join(data_path, file))
                    documents.extend(loader.load())
                except Exception as e:
                    print(f"Error loading {file}: {e}")
        
        # 2. Manejo de Fallo de Carga (Robustez)
        if not documents:
            print("Warning: No technical PDFs found in /data. Memory set to None.")
            self.vector_store = None
            self.retriever = None
            return

        # 3. Creación y Asignación
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=150)
        chunks = text_splitter.split_documents(documents)
        
        # Build searchable database

        self.vector_store = FAISS.from_documents(chunks, self.embeddings) 
        
        # self.retriever se asigna aquí
        self.retriever = self.vector_store.as_retriever(search_kwargs={"k": 5})
        print(f"Memory synced: {len(chunks)} technical segments loaded from Axalta TDS.")

    def search_manuals(self, query: str):
        """
        Busca contexto técnico y extrae el nombre de la fuente (metadata).
        """
        if self.vector_store is None:
             return "El motor de memoria no está cargado o sincronizado. Intente de nuevo en breve.", ""

        # Usamos retriever para obtener los documentos relevantes
        docs = self.vector_store.similarity_search(query, k=5)
        #docs = self.retriever.get_relevant_documents(query)

        # Inicializamos listas para el contenido y las fuentes
        context_list = []
        source_list = set() # Usamos un set para evitar fuentes duplicadas

        for doc in docs:
            context_list.append(doc.page_content)
            # Extraemos el nombre del archivo de los metadatos
            source_name = doc.metadata.get('source', 'Documento no citado')
            source_list.add(os.path.basename(source_name)) # Solo el nombre del archivo, no la ruta completa

        # El contexto que va a la IA es el texto unido
        context_for_ai = "\n---\n".join(context_list)

        # La lista de fuentes se convierte en una cadena para pasar a main.py
        sources_for_response = ", ".join(source_list)

        return context_for_ai, sources_for_response # Devolvemos dos valores