"""
    Agentic KPI Builder: 
    every function is annotated (@tool, @static, @prompt), orchestrated as nodes, 
    and resilient to errors.
    
    Jatin K Rai -- assignment
"""

from kpi.kpi_name_reference import KPINameReference
from kpi.kpi_loader import KPIOperationalEventLoader

class KPIInputHandler:
    """
    Handles user KPI input by delegating to KPINameReference.
    """

    def __init__(self, loader: KPIOperationalEventLoader):
        self.loader = loader

    def handle_input(self, kpi_name: str):
        reference = KPINameReference(self.loader)
        # Default intent schema; refined later by agent
        intent = {
            "kpi_name": kpi_name,
            "metric_type": "Count",
            "filters": "All Events",
            "aggregation": "Total",
            "time_period": "Monthly"
        }
        return reference.execute_intent(intent)
    
    
