"""
    Agentic KPI Builder: 
    every function is annotated (@tool, @static, @prompt), orchestrated as nodes, 
    and resilient to errors.
    
    Jatin K Rai -- assignment
"""

import streamlit as st
from kpi.kpi_name_reference import KPINameReference
from kpi.kpi_loader import KPIOperationalEventLoader
from kpi.kpi_input_handler import KPIInputHandler
from langchain_core.tools import tool
from kpi.kpi_agentic_tools_handler import KPIAgenticToolHandler
import uuid
from langchain_core.messages import HumanMessage

class KPIAgentHandler:
    """
    Agentic flow: guides user step by step from KPI name to computed result.
    Tracks conversation state across steps.
    """
  
    def __init__(self, data_file: str):
        self.reference = KPINameReference(data_file)
        
        if isinstance(data_file, KPIOperationalEventLoader):
            self.loader = data_file
        else:
            self.loader = KPIOperationalEventLoader(data_file)
        
        self.inputhandler = KPIInputHandler(self.loader)
        
        self.state = {
            "step": 0,
            "intent": {
                "kpi_name": None,
                "metric_type": None,
                "filters": None,
                "aggregation": None,
                "time_period": None
            }
        }
        if 'agentichandler' not in st.session_state:
            st.session_state.agentichandler = KPIAgenticToolHandler()
        
        
        
    #@tool("run_flow", description="run_flow Call")
    def run_flow(self):
        st.title("Agentic KPI Builder Assignment One")

        # Step 0: KPI name entry
        if self.state["step"] == 0:
            kpi_name = st.text_input("Enter KPI Name for evaluation on Operation events:")
            if kpi_name:
                st.write(f"Agent: You want KPI '{kpi_name}'. Let's refine definition.")
                self.state["intent"]["kpi_name"] = kpi_name
                self.state["step"] = 1

        # Step 1: Dynamic contextual questions
        if self.state["step"] == 1:
            st.subheader("Step 2: Define KPI Context")
            metric_type = st.radio("Metric type?", ["Count", "Sum", "Average", "Ratio"])
            filters = st.selectbox("Filters?", ["All Events"] + list(self.reference.df["event_type"].unique()) + list(self.reference.df["priority"].unique()))
            aggregation = st.radio("Aggregation?", ["Total", "Mean", "Max", "Min"])
            time_period = st.radio("Time period?", ["Daily", "Weekly", "Monthly", "Yearly"])
            if st.button("Submit Definition"):
                self.state["intent"].update({
                    "metric_type": metric_type,
                    "filters": filters,
                    "aggregation": aggregation,
                    "time_period": time_period
                })
                st.subheader("Structured KPI Intent")
                st.json(self.state["intent"])
                self.state["step"] = 2

        # Step 2: Compute KPI
        if self.state["step"] == 2:
            self.result = self.reference.execute_intent(self.state["intent"])
            st.subheader("Final KPI Result")
            st.json(self.result)
            return self.result
            #self.state["step"] = 3 #==> extension for this scenarios
            
        # Step 3: Agentic tools calling with invocation.
        if self.state["step"]== 3:
            try:
                user_input = self.state["intent"]["kpi_name"]
                if user_input:
                        thread_id = str(uuid.uuid4())
                        st.session_state.thread_id = thread_id
                        
                        messages = [HumanMessage(content=user_input)]
                        config = {'configurable': {'thread_id': thread_id}}

                      #  result = st.session_state.agentichandler.graph.invoke({'intent': self.state["intent"]}, config=config)
                        result = st.session_state.agentichandler.graph.invoke({'messages': messages}, config=config)
                        st.subheader('KPI Name information')
                        st.write(result['messages'][-1].content)
                        
                else:
                        st.error('Please enter a travel query.')

            except Exception as e:
                st.error(f'Error: {e}')
                


    def run_flowstatic(self):
        st.title("Agentic KPI Builder Assignment One")

        # Step 0: KPI name entry
        if self.state["step"] == 0:
            kpi_name = st.text_input("Enter KPI Name for evaluation on Operation events:")
            if kpi_name:
                st.write(f"Agent: You want KPI '{kpi_name}'. Let's refine definition.")
                self.state["intent"]["kpi_name"] = kpi_name
                self.state["step"] = 1

        # Step 1: Static contextual questions
        if self.state["step"] == 1:
           result = self.inputhandler.handle_input(self.state["intent"]["kpi_name"])
           st.subheader("Final KPI Result")
           st.json(result)
           return result