import pypdfium2 as pdfium
from sentence_transformers import SentenceTransformer
import numpy as np
import faiss # For vector store
from typing import Dict, Any, Callable
import camelot # For table extraction
import os
import pickle

class ChemicalEngineeringKnowledgeBase:
    """
    Represents a knowledge base for chemical engineering data.
    This is a simplified version; a real one would connect to databases,
    property estimation packages, etc.
    Can include structured data, property estimation, and RAG for documents.
    """
    def __init__(self, perrys_handbook_pdf_path: str = None, 
                 cache_dir: str = ".rag_cache",
                 force_reprocess: bool = False):
        """
        Initializes the Knowledge Base.

        Args:
            perrys_handbook_pdf_path (str, optional): Path to Perry's Handbook PDF
                                                      for RAG setup.
            cache_dir (str, optional): Directory to store cached RAG data.
            force_reprocess (bool, optional): If True, reprocess the PDF even if a cache exists.
        """
        self.data_sources: list[str] = ["NIST", "Perry's Handbook", "CRC Handbook"]
        # In a real system, this might load/connect to databases or property estimation models.

        self.embedding_model = None
        self.vector_store = None
        self.text_chunks = []
        self.pdf_path = perrys_handbook_pdf_path
        self.cache_dir = cache_dir
        os.makedirs(self.cache_dir, exist_ok=True) # Ensure cache directory exists

        if perrys_handbook_pdf_path:
            self.data_sources.append(f"Perry's Handbook PDF: {perrys_handbook_pdf_path}")
           
           # Define cache file paths
            pdf_filename = os.path.basename(perrys_handbook_pdf_path)
            chunks_cache_path = os.path.join(self.cache_dir, f"{pdf_filename}_chunks.pkl")
            faiss_cache_path = os.path.join(self.cache_dir, f"{pdf_filename}_vector_store.faiss")

            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2') # Load a pre-trained model

            if not force_reprocess and os.path.exists(chunks_cache_path) and os.path.exists(faiss_cache_path):
                print(f"Loading RAG data from cache for {pdf_filename}...")
                try:
                    with open(chunks_cache_path, 'rb') as f:
                        self.text_chunks = pickle.load(f)
                    self.vector_store = faiss.read_index(faiss_cache_path)
                    print(f"Successfully loaded {len(self.text_chunks)} chunks and FAISS index from cache.")
                except Exception as e:
                    print(f"Error loading from cache: {e}. Reprocessing PDF.")
                    self._initialize_and_build_rag(perrys_handbook_pdf_path, chunks_cache_path, faiss_cache_path)
            else:
                print(f"No cache found or force_reprocess=True for {pdf_filename}. Processing PDF...")
                self._initialize_and_build_rag(perrys_handbook_pdf_path, chunks_cache_path, faiss_cache_path)

    def _initialize_and_build_rag(self, pdf_path: str, chunks_cache_path: str, faiss_cache_path: str):
        """Helper to process PDF, build RAG, and save to cache."""
        try:
            print(f"Initializing RAG system with PDF: {pdf_path}...")
            self._load_and_index_pdf(pdf_path) # This will populate self.text_chunks and self.vector_store
            
            if self.text_chunks and self.vector_store:
                print(f"Saving {len(self.text_chunks)} chunks to cache: {chunks_cache_path}")
                with open(chunks_cache_path, 'wb') as f:
                    pickle.dump(self.text_chunks, f)
                
                print(f"Saving FAISS index to cache: {faiss_cache_path}")
                faiss.write_index(self.vector_store, faiss_cache_path)
                print("RAG system initialized and cached successfully.")
            else:
                print("RAG initialization failed: No chunks or vector store created.")
                self.embedding_model = None # Ensure it's None if setup fails
        except Exception as e:
            print(f"Error initializing RAG system: {e}")
            self.embedding_model = None # Ensure it's None if setup fails

        
    def _load_and_index_pdf(self, pdf_path: str, chunk_size: int = 500, chunk_overlap: int = 50):
        """
        Loads a PDF, extracts text, chunks it, creates embeddings, and indexes them.
        """
        # 1. Load PDF and extract text
        print("Loading PDF, extracting text and tables...")
        all_content_chunks = [] # Will store both text and table-derived chunks
        processed_pages = 0
        tables_found_count = 0
        try:
            pdf_doc = pdfium.PdfDocument(pdf_path)
            for i in range(len(pdf_doc)):
                page_text_content = ""
                page = pdf_doc.get_page(i)

                # Attempt to extract tables from the current page using Camelot
                try:
                    # Camelot needs the PDF path or a file-like object.
                    # For a single page, it's often easier to pass the whole PDF path and page number.
                    tables = camelot.read_pdf(pdf_path, pages=str(i + 1), flavor='lattice', suppress_stdout=True) # Try 'stream' if 'lattice' fails
                    # You might want to add a fallback to try 'stream' if 'lattice' returns no tables or errors.
                    if not tables:
                        tables = camelot.read_pdf(pdf_path, pages=str(i + 1), flavor='stream', suppress_stdout=True)

                    for table_idx, table in enumerate(tables):
                        table_df = table.df
                        if not table_df.empty:
                            # Convert table to Markdown for better structural representation
                            table_markdown = table_df.to_markdown(index=False)
                            tables_found_count += 1
                            table_text = f"Table on page {i+1}, table index {table_idx}:\n{table_markdown}"
                            all_content_chunks.append(table_text.strip())
                except Exception as e:
                    print(f"Warning: Could not extract tables from page {i+1} with Camelot: {e}")

                # Extract regular text from the page
                textpage = page.get_textpage()
                page_text_content = textpage.get_text_range()
                textpage.close()
                page.close()

                # Simple chunking for page text (you might want to integrate this with table boundaries)
                if page_text_content.strip():
                    # Basic split by paragraphs for non-table text, then your word-based chunking
                    paragraphs = page_text_content.split('\n\n')
                    for para_idx, para in enumerate(paragraphs):
                        if para.strip():
                            words = para.split()
                            for j in range(0, len(words), chunk_size - chunk_overlap):
                                chunk = " ".join(words[j:j + chunk_size])
                                all_content_chunks.append(chunk)
                processed_pages += 1
                if processed_pages % 10 == 0:
                    print(f"Processed {processed_pages} pages...")
            pdf_doc.close()
        except Exception as e:
            raise RuntimeError(f"Failed to load or parse PDF {pdf_path}: {e}")

        self.text_chunks = [chunk for chunk in all_content_chunks if chunk.strip()] # Store all processed chunks

        # Original chunking logic is now integrated above, per page, after table extraction.
        # The self.text_chunks list will now contain a mix of text chunks and table representations.
        print(f"Total text/table chunks extracted: {len(self.text_chunks)}")
        
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
    # e.g., create a simple "test_doc.pdf" with some chemical engineering text in the same directory,
    # or provide an absolute path to a larger PDF like Perry's Handbook.
    # Example of an absolute path (Windows):
    # pdf_file_path = r"C:\Users\YourUsername\Documents\Perry_Handbook_8th_Edition.pdf"
    # Example for a file in a 'data' subdirectory relative to this script:
    # pdf_file_path = "data/perry.pdf" 
    
    # !!! YOU MUST PROVIDE A VALID PATH TO A PDF FOR RAG TO WORK !!!
    pdf_file_path = r"data/perry.pdf" # Set this to a valid path to your PDF, e.g., "data/perry.pdf"

    if not pdf_file_path:
        print("PDF path not set. Skipping RAG initialization and testing.")
        print(f"To test RAG, set 'pdf_file_path' in the __main__ block of {__file__}")
    elif not os.path.exists(pdf_file_path):
        print(f"PDF file not found at '{pdf_file_path}'. Skipping RAG initialization and testing.")
    else:
        kb_with_rag = ChemicalEngineeringKnowledgeBase(perrys_handbook_pdf_path=pdf_file_path, force_reprocess=False) # Set force_reprocess=True to ignore cache
        if kb_with_rag.vector_store:
            print("\n--- RAG Query Example ---")
            query = "What are the principles of distillation?"
            relevant_chunks = kb_with_rag.query_document_rag(query, k=2)
            print(f"Query: {query}")
            for i, chunk in enumerate(relevant_chunks):
                print(f"\nRelevant Chunk {i+1}:\n{chunk[:300]}...") # Print first 300 chars
        else:
            print(f"Could not initialize RAG. Ensure '{pdf_file_path}' is a valid PDF.")
