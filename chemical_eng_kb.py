import pypdfium2 as pdfium
from sentence_transformers import SentenceTransformer
import numpy as np
import faiss # For vector store
from typing import Dict, Any, Callable

class ChemicalEngineeringKnowledgeBase:
    """
    Represents a knowledge base for chemical engineering data.
    This is a simplified version; a real one would connect to databases,
    property estimation packages, etc.
    Can include structured data, property estimation, and RAG for documents.
    """
    def __init__(self, perrys_handbook_pdf_path: str = None):
        """
        Initializes the Knowledge Base.

        Args:
            perrys_handbook_pdf_path (str, optional): Path to Perry's Handbook PDF
                                                      for RAG setup.
        """
        self.data_sources: list[str] = ["NIST", "Perry's Handbook", "CRC Handbook"]
        # In a real system, this might load/connect to databases or property estimation models.

        self.embedding_model = None
        self.vector_store = None
        self.text_chunks = []

        if perrys_handbook_pdf_path:
            self.data_sources.append(f"Perry's Handbook PDF: {perrys_handbook_pdf_path}")
            try:
                print(f"Initializing RAG system with PDF: {perrys_handbook_pdf_path}...")
                self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2') # A good general-purpose model
                self._load_and_index_pdf(perrys_handbook_pdf_path)
                print("RAG system initialized successfully.")
            except Exception as e:
                print(f"Error initializing RAG system: {e}")
                self.embedding_model = None # Ensure it's None if setup fails

    def _load_and_index_pdf(self, pdf_path: str, chunk_size: int = 500, chunk_overlap: int = 50):
        """
        Loads a PDF, extracts text, chunks it, creates embeddings, and indexes them.
        """
        # 1. Load PDF and extract text
        print("Loading PDF and extracting text...")
        full_text = ""
        try:
            pdf_doc = pdfium.PdfDocument(pdf_path)
            for i in range(len(pdf_doc)):
                page = pdf_doc.get_page(i)
                textpage = page.get_textpage()
                full_text += textpage.get_text_range() + "\n"
                textpage.close()
                page.close()
            pdf_doc.close()
        except Exception as e:
            raise RuntimeError(f"Failed to load or parse PDF {pdf_path}: {e}")

        if not full_text.strip():
            raise ValueError("No text extracted from PDF. It might be image-based or empty.")

        # 2. Chunk text
        print("Chunking text...")
        words = full_text.split()
        for i in range(0, len(words), chunk_size - chunk_overlap):
            chunk = " ".join(words[i:i + chunk_size])
            self.text_chunks.append(chunk)

        if not self.text_chunks:
            raise ValueError("Text chunking resulted in no chunks.")

        # 3. Embed chunks
        print(f"Embedding {len(self.text_chunks)} chunks...")
        chunk_embeddings = self.embedding_model.encode(self.text_chunks, show_progress_bar=True)

        # 4. Build FAISS index (Vector Store)
        print("Building FAISS index...")
        dimension = chunk_embeddings.shape[1]
        self.vector_store = faiss.IndexFlatL2(dimension) # Using L2 distance
        self.vector_store.add(np.array(chunk_embeddings, dtype=np.float32))

    def get_fluid_property(self, fluid_name: str, property_name: str, conditions: Dict[str, Any] = None) -> Any:
        """
        Illustrative method to retrieve a fluid property from structured sources.
        In a real system, this would query a database or use correlations.
        This method is NOT using the RAG system for precise numerical lookups yet.
        """
        # print(f"[KnowledgeBase] INFO: Attempting to retrieve {property_name} for {fluid_name} at {conditions or {}}}.")
        if fluid_name.lower() == "water" and property_name.lower() == "density_kg_m3":
            return 1000.0 # kg/m^3
        if fluid_name.lower() == "water" and property_name.lower() == "viscosity_pa_s":
            return 0.001  # Pa.s
        return None # Property not found or not implemented for this example

    def query_document_rag(self, query_text: str, k: int = 3) -> list[str]:
        """
        Queries the indexed PDF document using RAG principles (retrieval part).

        Args:
            query_text: The natural language query.
            k: The number of top relevant chunks to retrieve.

        Returns:
            A list of relevant text chunks from the document.
        """
        if not self.vector_store or not self.embedding_model:
            return ["RAG system not initialized or PDF not processed."]

        query_embedding = self.embedding_model.encode([query_text])
        distances, indices = self.vector_store.search(np.array(query_embedding, dtype=np.float32), k)
        
        return [self.text_chunks[i] for i in indices[0]]

# Example Usage (for testing ChemicalEngineeringKnowledgeBase directly)
if __name__ == "__main__":
    # IMPORTANT: Replace with an actual path to a PDF file for testing.
    # Create a dummy PDF for testing if you don't have Perry's handy for this example.
    # e.g., create a simple "test_handbook.pdf" with some chemical engineering text.
    pdf_file_path = r"C:/Users/luisr/python_projects/chem_eng_agents/data/perry.pdf" # <--- !!! REPLACE THIS !!!

    # For testing without a real PDF, you can comment out the RAG part:
    # kb = ChemicalEngineeringKnowledgeBase()
    # print(kb.get_fluid_property("water", "density_kg_m3"))

    try:
        # Test with RAG
        kb_with_rag = ChemicalEngineeringKnowledgeBase(perrys_handbook_pdf_path=pdf_file_path)
        if kb_with_rag.vector_store:
            print("\n--- RAG Query Example ---")
            query = "What are the principles of distillation?"
            relevant_chunks = kb_with_rag.query_document_rag(query, k=2)
            print(f"Query: {query}")
            for i, chunk in enumerate(relevant_chunks):
                print(f"\nRelevant Chunk {i+1}:\n{chunk[:300]}...") # Print first 300 chars
        else:
            print(f"Could not initialize RAG. Ensure '{pdf_file_path}' is a valid PDF.")

    except FileNotFoundError:
        print(f"Error: PDF file not found at '{pdf_file_path}'. Please provide a valid path.")
    except RuntimeError as e:
        print(f"Runtime error during RAG initialization: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")