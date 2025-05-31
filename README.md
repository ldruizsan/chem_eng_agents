# AI Agents for Chemical Engineering

## Project Goal
The purpose of this project is to create a swarm of intelligent agents specializing in different areas of chemical engineering. A master agent will orchestrate these agents, taking user queries, parsing them, and delegating tasks to the appropriate specialized agent.

There is also a RAG system in place that will serve as a source of truth for all agents to interact with.

*   **Structured Data Access:** Provides methods to retrieve specific data points, such as fluid properties (currently illustrative, e.g., density and viscosity of water).
*   **Retrieval Augmented Generation (RAG) for PDF Documents:**
    *   **Dependencies:** `pypdfium2`, `sentence-transformers`, `faiss-cpu`, `numpy`.
    *   **PDF Ingestion:** Can load, parse, and extract text from PDF documents (e.g., Perry's Handbook).
    *   **Table Extraction:** Uses `camelot-py` to attempt extraction of tables from PDFs, converting them to Markdown for better semantic representation.
    *   **Text Chunking:** Splits the extracted text into manageable chunks.
    *   **Embedding:** Uses `sentence-transformers` (specifically `all-MiniLM-L6-v2`) to generate semantic embeddings for text chunks.
    *   **Vector Store:** Employs `FAISS` (IndexFlatL2) to store and efficiently search these embeddings.
    *   **Caching:** Implements caching for processed chunks and the FAISS index to speed up subsequent initializations.
    *   **Querying:** Allows natural language queries against the indexed PDF content, retrieving the most relevant text chunks.

**File:** `chemical_eng_agents/chemical_eng_kb.py`

### 2. Specialized Agents (LLM-Driven with RAG)

All specialized agents (`FluidMechanicsAgent`, `HeatTransferAgent`, `ReactorDesignAgent`) now follow a consistent, LLM-driven architecture:

*   **Initialization:** Each agent is initialized with a shared `ChemicalEngineeringKnowledgeBase` instance and a conceptual `llm_client`.
*   **Persona-Driven Prompts:** Each agent constructs a detailed prompt for an LLM, imbuing it with a specific expert persona (e.g., "Fluid Mechanics Expert").
*   **RAG Integration:** Before querying the LLM, the agent retrieves relevant context chunks from the `ChemicalEngineeringKnowledgeBase` using the user's task description. This context is included in the LLM prompt.
*   **Task Execution:** The agent sends the combined prompt (persona + RAG context + user query) to the LLM and returns the LLM's generated response.
*   **Simplified Logic:** The agents no longer contain hard-coded calculation methods; they rely on the LLM's capabilities, guided by the persona and RAG context.

#### a. `FluidMechanicsAgent`
Specializes in fluid mechanics problems.

**File:** `chemical_eng_agents/fluid_mech_agent.py`

#### b. `HeatTransferAgent`
Specializes in heat transfer calculations and problems.

**File:** `chemical_eng_agents/heat_transfer_agent.py`

#### c. `ReactorDesignAgent`
Focuses on chemical reactor design, kinetics, and sizing.

**File:** `chemical_eng_agents/reactor_design_agent.py`

## How to Run & Test

### Testing the `ChemicalEngineeringKnowledgeBase` (RAG Capabilities)
1.  **Prerequisites:** Ensure you have the necessary Python packages installed:
    ```bash
    pip install pypdfium2 sentence-transformers faiss-cpu numpy pandas camelot-py[cv] ghostscript
    ```
2.  **Prepare a PDF:** Place a PDF document (e.g., a section of Perry's Handbook or a test chemical engineering document) in a known location (e.g., a `data` subfolder).
3.  **Update Path:** Modify the `pdf_file_path` variable in the `if __name__ == "__main__":` block of `chemical_eng_agents/chemical_eng_kb.py` to point to your PDF file.
    ```python
    # In chemical_eng_agents/chemical_eng_kb.py
    pdf_file_path = os.path.join("data", "perry.pdf") # Example
    ```
4.  **Run the Script:**
    ```bash
    python chemical_eng_agents/chemical_eng_kb.py
    ```
    This will initialize the RAG system (caching results for faster subsequent runs) and run example queries.

### Testing Specialized Agents (Conceptual LLM Interaction)
Each agent file (`fluid_mech_agent.py`, `heat_transfer_agent.py`, `reactor_design_agent.py`) contains an `if __name__ == "__main__":` block for testing.
1.  **Prerequisites:** Same as for `ChemicalEngineeringKnowledgeBase`.
2.  **LLM Client:** These tests currently use a `MockLLMClient`. For full functionality, you'll need to implement and integrate a real LLM client.
3.  **Update PDF Path:** Ensure the `pdf_path_for_kb` in the agent's `__main__` block points to your test PDF if you want RAG context to be used.
4.  **Run the Agent Script:**
    ```bash
    python chemical_eng_agents/fluid_mech_agent.py
    ```
    This will instantiate the `FluidMechanicsAgent` with the knowledge base and execute predefined example tasks.
    This will instantiate the `FluidMechanicsAgent` (and potentially placeholders for other agents if you uncomment them in the script's `if __name__ == "__main__":` block) with the shared knowledge base and execute predefined example tasks for the `FluidMechanicsAgent`.

    Example of how other agents would be instantiated in `fluid_mech_agent.py` or a master script:
    ```python
    # ht_agent = HeatTransferAgent(knowledge_base=shared_knowledge_base)
    # rd_agent = ReactorDesignAgent(knowledge_base=shared_knowledge_base)
    ```

## Dependencies


## Future Work

*   **Develop other specialized agents:**
*   Heat Transfer Agent
*   Reactor Design Agent
*   **Develop specialized agents:**
    *   Implement `HeatTransferAgent`
    *   Implement `ReactorDesignAgent`
*   **Implement the Master Agent:** For orchestrating tasks and managing communication between agents.
*   **Enhance `_parse_task`:** Implement more sophisticated NLP for robust task understanding and parameter extraction.
*   **Expand `ChemicalEngineeringKnowledgeBase`**
