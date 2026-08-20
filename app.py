"""
    Agentic KPI Builder: 
    every function is annotated (@tool, @static, @prompt), orchestrated as nodes, 
    and resilient to errors.
    
    Jatin K Rai -- assignment
    
    Agentic Flow: Each function is a node in the LangGraph workflow.
    Dynamic Questions: Derived from dataset columns, not hardcoded.
    Intent & Schema: JSON built and validated by validate_intent.
    KPI Calculation: Executed dynamically via loader methods.
    Review Card UX: Styled output with status badge.
    Self‑Healing: Errors route back to agent questions or fallback LLM.
    
    SelfHealing Flow
    If validate_intent returns errors → route back to run_flow to re‑ask.
    If execute_intent fails (no method found) → call groq_llm_response.
    If groq_llm_response fails (API unavailable) → fallback to static description.
"""

import streamlit as st
from kpi.review_card_generator import ReviewCardGenerator
from kpi.kpi_name_reference import KPINameReference
import uuid
from langchain_core.messages import HumanMessage

def load_css(file_path: str):
    """Utility to load and apply CSS styles."""
    with open(file_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
        
                

def main():
    st.set_page_config(page_title="Agentic KPI Builder", layout="wide")

    # Apply custom CSS
    load_css("assets/styles.css")

    st.sidebar.title("Agentic KPI Builder")
    st.sidebar.info("Guided agentic flow from KPI name → intent → computation → review card.")

    review = ReviewCardGenerator("data/operations_events.csv")
    review.run_review_card()
    
    objKPINameReference = KPINameReference("data/operations_events.csv")
    objKPINameReference.groq_llm_response("ResolutionRateMicrosoft")
    
if __name__ == "__main__":
    main()
