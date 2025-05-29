from typing import Dict, Any, Callable
from chemical_eng_agents.chemical_eng_kb import ChemicalEngineeringKnowledgeBase # Assuming chemical_eng_kb.py is in this path
class FluidMechanicsAgent:
    """
    An agent specializing in fluid mechanics calculations.
    """
    def __init__(self, knowledge_base: ChemicalEngineeringKnowledgeBase):
        """
        Initializes the FluidMechanicsAgent with available calculation methods
        and a shared knowledge base.

        Args:
            knowledge_base: An instance of ChemicalEngineeringKnowledgeBase.
        """
        self.knowledge_base: ChemicalEngineeringKnowledgeBase = knowledge_base
        self.capabilities: Dict[str, Callable[[Dict[str, Any]], Dict[str, Any]]] = {
            "pressure_drop": self._calculate_pressure_drop,
            "flow_regime": self._determine_flow_regime,
            # ... other fluid mechanics methods
        }
        # self.data_sources is now part of self.knowledge_base

    def _parse_task(self, task_description: str) -> Dict[str, Any]:
        """
        Parses the task description to identify the task type and extract parameters.
        This is a simplified parser. A real-world implementation would likely use
        more sophisticated NLP techniques or expect structured input.

        Args:
            task_description: A natural language string describing the task.

        Returns:
            A dictionary containing 'task_type' and 'parameters'.
        """
        task_description_lower = task_description.lower()

        # Illustrative: Attempt to get default fluid properties.
        # In a real system, fluid name and conditions would be extracted from task_description.
        fluid_name = "water" # Assume default or could be extracted
        density = self.knowledge_base.get_fluid_property(fluid_name, "density_kg_m3")
        viscosity = self.knowledge_base.get_fluid_property(fluid_name, "viscosity_Pa_s")

        # Default/Illustrative parameters. A more sophisticated parser or
        # the master agent would be responsible for extracting these from the user query.
        extracted_params = {
            "diameter_m": 0.1,          # meters
            "flow_rate_m3_s": 0.05,     # m^3/s
            "velocity_m_s": 0.637,      # m/s (derived from flow_rate and diameter for consistency)
            "density_kg_m3": density if density is not None else 1000.0, # Fallback
            "viscosity_Pa_s": viscosity if viscosity is not None else 0.001, # Fallback
            "length_m": 100.0,          # meters
            "roughness_m": 0.000045,    # meters (e.g., commercial steel)
            "fluid_name": fluid_name
        }

        if "pressure drop" in task_description_lower:
            return {"task_type": "pressure_drop", "parameters": extracted_params}
        elif "flow regime" in task_description_lower:
            return {"task_type": "flow_regime", "parameters": extracted_params}
        # ... other task types could be identified here

        return {"task_type": "unknown", "parameters": {"original_task": task_description}}

    def execute_task(self, task_description: str) -> Dict[str, Any]:
        """
        Executes a fluid mechanics task based on its description.

        Args:
            task_description: A string describing the task to be performed.

        Returns:
            A dictionary containing the status and result of the task execution.
        """
        parsed_task = self._parse_task(task_description)
        task_type = parsed_task.get("task_type")
        params = parsed_task.get("parameters")

        if task_type in self.capabilities:
            calculation_method = self.capabilities[task_type]
            try:
                result_data = calculation_method(params)
                return {"status": "success", "task": task_type, "result": result_data}
            except ValueError as ve: # Catch specific, expected errors
                return {"status": "error", "task": task_type, "message": f"Parameter error: {str(ve)}"}
            except Exception as e: # Catch unexpected errors during calculation
                return {"status": "error", "task": task_type, "message": f"Calculation error: {str(e)}"}
        else:
            return {"status": "error", "task": task_type, "message": f"Unknown task type: '{task_type}'"}

    def _calculate_pressure_drop(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculates pressure drop. (Illustrative - uses placeholder logic)
        A real implementation would use equations like Darcy-Weisbach or Bernoulli.
        """
        required_keys = ["density_kg_m3", "velocity_m_s", "length_m", "diameter_m", "viscosity_Pa_s", "roughness_m"]
        if not all(key in params for key in required_keys):
            missing_keys = [key for key in required_keys if key not in params]
            raise ValueError(f"Missing required parameters for pressure drop: {', '.join(missing_keys)}")

        # Placeholder for a more complex calculation (e.g., Darcy-Weisbach)
        # For simplicity, let's imagine a very simplified calculation:
        # Pressure Drop = f * (L/D) * (rho * V^2 / 2)
        # Here, 'f' (friction factor) would itself be a complex calculation.
        # We'll use a dummy value.
        friction_factor = 0.02 # Dummy friction factor; could be calculated based on Re and roughness

        # Potentially use self.knowledge_base here if more detailed properties are needed
        # for friction factor calculation, beyond what's in params.
        # For example: self.knowledge_base.get_specific_friction_model_params(...)

        pressure_drop_Pa = (friction_factor * (params["length_m"] / params["diameter_m"]) *
                            (params["density_kg_m3"] * params["velocity_m_s"]**2 / 2))

        return {"pressure_drop_Pa": pressure_drop_Pa, "unit": "Pa", "method": "Darcy-Weisbach (simplified)"}

    def _determine_flow_regime(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Determines the flow regime based on the Reynolds number.
        """
        required_keys = ["density_kg_m3", "velocity_m_s", "diameter_m", "viscosity_Pa_s"]
        if not all(key in params for key in required_keys):
            missing_keys = [key for key in required_keys if key not in params]
            raise ValueError(f"Missing required parameters for flow regime: {', '.join(missing_keys)}")

        if params["viscosity_Pa_s"] == 0:
            raise ValueError("Viscosity cannot be zero for Reynolds number calculation.")

        reynolds_number = (params["density_kg_m3"] * params["velocity_m_s"] *
                           params["diameter_m"]) / params["viscosity_Pa_s"]

        if reynolds_number < 2300:
            regime = "laminar"
        elif reynolds_number < 4000:
            regime = "transitional"
        else:
            regime = "turbulent"

        return {"reynolds_number": round(reynolds_number, 2), "flow_regime": regime}

# Example Usage (for testing purposes)
if __name__ == "__main__":
    # Create a single instance of the knowledge base
    # IMPORTANT: Replace with an actual path to your Perry's Handbook PDF or other relevant PDF.
    # If you don't provide a path, RAG features for that PDF won't be initialized.
    pdf_path_for_kb = "path_to_your_perrys_handbook.pdf" # <--- !!! REPLACE THIS !!!
    # You might want to handle the case where the PDF is not found more gracefully
    shared_knowledge_base = ChemicalEngineeringKnowledgeBase(perrys_handbook_pdf_path=pdf_path_for_kb)

    # Pass the shared knowledge base to the agent(s)
    fm_agent = FluidMechanicsAgent(knowledge_base=shared_knowledge_base)
    task1_desc = "Calculate the pressure drop in the pipe."
    result1 = fm_agent.execute_task(task1_desc)
    print(f"Task: {task1_desc}\nResult: {result1}\n")

    task2_desc = "Determine the flow regime."
    result2 = fm_agent.execute_task(task2_desc)
    print(f"Task: {task2_desc}\nResult: {result2}\n")

    task3_desc = "What is the heat capacity of water?" # Unknown task
    result3 = fm_agent.execute_task(task3_desc)
    print(f"Task: {task3_desc}\nResult: {result3}\n")

    # Example of a task that might cause a parameter error if _parse_task wasn't providing defaults
    # For this, we'd need to modify _parse_task to not always provide all params or pass them directly
    # fm_agent.capabilities["pressure_drop"]({}) # This would raise ValueError