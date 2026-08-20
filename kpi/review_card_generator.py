"""
    Agentic KPI Builder: 
    every function is annotated (@tool, @static, @prompt), orchestrated as nodes, 
    and resilient to errors.
    
    Jatin K Rai -- assignment
"""
import streamlit as st
from kpi.kpi_agent_handler import KPIAgentHandler
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph

class ReviewCardGenerator:
    """
    Displays KPI Review Card after agentic flow completes.
    """

    def __init__(self, data_file: str):
        self.agent = KPIAgentHandler(data_file)
        
    #@staticmethod
    def compute_status_badge(self, kpi_name, value):
        if value is None:
            return "Critical"
        if "Ratio" in kpi_name:
            return "Good" if value < 0.5 else "Warning" if value < 1.0 else "Critical"
        if "Count" in kpi_name:
            return "Good" if value == 0 else "Warning" if value < 5 else "Critical"
        if "Average" in kpi_name or "Hours" in kpi_name:
            return "Good" if value < 10 else "Warning" if value < 20 else "Critical"
        return "Warning"
    

    def run_review_card(self):
        st.title("KPI Review Card")
        result = self.agent.run_flow()
        #Considered dynamics only.
        #result = self.agent.run_flowstatic()

        if result and "Error" not in result:
            kpi_name = result.get("KPIName")
            val = result.get("ComputedValue")
            formula = result.get("Formula", "N/A")
            unit = "events" if result.get("MetricType") == "Count" else "hours" if result.get("MetricType") == "Average" else "ratio"
            badge = self.compute_status_badge(kpi_name, val)

            # Styled card
            st.markdown(
                f"""
                <div class="card">
                    <h3>{kpi_name}</h3>
                    <p><b>Description:</b> {result.get('Description','Derived from dataset')}</p>
                    <p><b>Formula:</b> {formula}</p>
                    <p><b>Computed Value:</b> {val}</p>
                    <p><b>Unit:</b> {unit}</p>
                    <span class="badge {badge.lower()}">{badge}</span>
                </div>
                """,
                unsafe_allow_html=True
            )

            if result.get("MetricType") == "Ratio":
                st.write(f"**Numerator:** {result['Numerator']}")
                st.write(f"**Denominator:** {result['Denominator']}")

            # Action buttons
            col1, col2, col3 = st.columns(3)
            approve_btn = col1.button("Approve", disabled=(val is None))
            edit_btn = col2.button("Edit")
            regen_btn = col3.button("Regenerate")

            if approve_btn:
                st.success("KPI Approved.")
            if edit_btn:
                self.agent.state["step"] = 1
            if regen_btn:
                self.agent.state = {"step": 0, "intent": {}}
                st.experimental_rerun()

        elif result and "Error" in result:
            st.error(f"KPI validation failed: {result['Error']}")
