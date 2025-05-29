class ReactorDesignAgent:
    def __init__(self):
        self.reactor_types = ["CSTR", "PFR", "Batch"]
        self.kinetics_db = "Arrhenius_parameters.csv"
    
    def execute_task(self, task_description):
        if "CSTR" in task_description:
            return self._design_cstr(task_description)
        elif "PFR" in task_description:
            return self._design_pfr(task_description)
        # ... other cases
    
    def _design_cstr(self, params):
        # Solve CSTR design equations
        return f"CSTR Volume: {volume} m³, Conversion: {conversion}%"