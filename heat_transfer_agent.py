class HeatTransferAgent:
    def __init__(self):
        self.methods = {
            "LMTD": self._calculate_lmtd,
            "NTU": self._calculate_ntu,
            # ... other heat transfer methods
        }
    
    def execute_task(self, task_description):
        if "heat exchanger" in task_description:
            return self.methods["LMTD"](task_description)
        elif "heat coefficient" in task_description:
            return self._estimate_heat_coefficient(task_description)
        # ... other cases
    
    def _calculate_lmtd(self, params):
        # Log Mean Temperature Difference method
        return f"Required heat transfer area: {area} m²"