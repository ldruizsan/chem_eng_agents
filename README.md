# AI Agents for Chemical Engineering

## Goal
The purpose of this project is to create a swarm of agents specializing in different areas of chemical engineering. There will be a master agent that will serve as an orchestrator and will take the user query, parse it, and figure out the agents it needs to perform the task.

There is also a RAG system in place that will serve as a source of truth for all agents to interact with.

*   **Structured Data Access:** Provides methods to retrieve specific data points, such as fluid properties (currently illustrative, e.g., density and viscosity of water).
*   **Retrieval Augmented Generation (RAG) for PDF Documents:**
    *   **Dependencies:** `pypdfium2`, `sentence-transformers`, `faiss-cpu`, `numpy`.
    *   **PDF Ingestion:** Can load, parse, and extract text from PDF documents (e.g., Perry's Handbook).
    *   **Text Chunking:** Splits the extracted text into manageable chunks.
    *   **Embedding:** Uses `sentence-transformers` (specifically `all-MiniLM-L6-v2`) to generate semantic embeddings for text chunks.

**File:** `chemical_eng_agents/fluid_mech_agent.py`

### 3. `HeatTransferAgent` (Placeholder)

This agent will specialize in heat transfer calculations and problems.
*(Currently a placeholder, to be developed).*

**File:** `chemical_eng_agents/heat_transfer_agent.py` (To be created)

### 4. `ReactorDesignAgent` (Placeholder)

This agent will focus on chemical reactor design, kinetics, and sizing.
*(Currently a placeholder, to be developed).*

**File:** `chemical_eng_agents/reactor_design_agent.py` (To be created)

## How to Run & Test

### Testing the `ChemicalEngineeringKnowledgeBase` (RAG Capabilities)
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
