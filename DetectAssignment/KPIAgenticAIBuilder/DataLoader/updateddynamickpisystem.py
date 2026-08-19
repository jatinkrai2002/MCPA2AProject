# kpi_system.py
import streamlit as st
import pandas as pd
import inspect
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
import os
from langchain_core.messages import HumanMessage

# ------------------------------
# Loader: reads and validates CSV, exposes KPI methods dynamically
# ------------------------------
class KPIOperationalEventLoader:
    def __init__(self, csv_file: str):
        self.df = pd.read_csv(csv_file)
        self.validate_data()

    def validate_data(self):
        # Ensure numeric columns are properly typed
        for col in ["cost_amount","processing_hours","customer_count"]:
            if col in self.df.columns:
                self.df[col] = pd.to_numeric(self.df[col], errors="coerce").fillna(0)

    # Example KPI methods (extendable)
    def IssueCount(self):
        return len(self.df[self.df["event_type"]=="Issue"])

    def NearMissCount(self):
        return len(self.df[self.df["event_type"]=="Near Miss"])

    def AverageProcessingHours(self):
        return self.df["processing_hours"].mean()


# ------------------------------
# Backend: validates and executes KPI intents
# ------------------------------
class KPINameReference:
    def __init__(self, loader_or_file):
        if isinstance(loader_or_file, KPIOperationalEventLoader):
            self.loader = loader_or_file
        else:
            self.loader = KPIOperationalEventLoader(loader_or_file)
        self.df = self.loader.df

    def validate_intent(self, intent: dict):
        errors = []
        required_fields = ["kpi_name","metric_type","filters","aggregation","time_period"]
        for f in required_fields:
            if f not in intent:
                errors.append(f"Missing required field: {f}")
        return errors

    def execute_intent(self, intent: dict):
        errors = self.validate_intent(intent)
        if errors:
            return {"Error": errors}

        kpi_name = intent["kpi_name"]
        # Check if KPIName matches a loader method
        methods = {name: func for name, func in inspect.getmembers(self.loader, predicate=inspect.ismethod)}
        if kpi_name in methods:
            try:
                result = methods[kpi_name]()
                return {
                    "KPIName": kpi_name,
                    "MetricType": intent["metric_type"],
                    "Filters": intent["filters"],
                    "Aggregation": intent["aggregation"],
                    "TimePeriod": intent["time_period"],
                    "ComputedValue": result,
                    "Formula": f"Derived from loader method {kpi_name}"
                }
            except Exception as e:
                return {"Error": str(e)}

        # Otherwise fallback to Groq LLM for description
        os.environ["GROQ_API_KEY"] = "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"
        os.environ["LANGSMITH_API_KEY"] = "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"
        groq_llm = ChatGroq(model="llama-3.1-8b-instant")
        prompt = ChatPromptTemplate.from_messages([
            ("system","You are an expert KPI analyst. Provide concise explanations."),
            ("human",f"Explain in 2-3 lines what KPI '{kpi_name}' could represent in operational analytics.")
        ])
        chain = prompt | groq_llm
        response = chain.invoke({})
        return {
            "KPIName": kpi_name,
            "Description": response.content
        }


# ------------------------------
# Agent: guides user step by step
# ------------------------------
class KPIAgentHandler:
    def __init__(self, data_file: str):
        self.reference = KPINameReference(data_file)
        self.state = {"step":0,"intent":{}}

    def run_flow(self):
        st.title("Agentic KPI Handler")

        # Step 0: KPI name entry
        if self.state["step"]==0:
            kpi_name = st.text_input("Enter KPI Name:")
            if kpi_name:
                st.write(f"Agent: You want KPI '{kpi_name}'. Let's refine definition.")
                self.state["intent"]["kpi_name"]=kpi_name
                self.state["step"]=1

        # Step 1: Dynamic questions based on dataset
        if self.state["step"]==1:
            st.subheader("Step 2: Define KPI Context")
            metric_type = st.radio("Metric type?", ["Count","Sum","Average","Ratio"])
            filters = st.selectbox("Filters?", ["All Events"]+list(self.reference.df["event_type"].unique())+list(self.reference.df["priority"].unique()))
            aggregation = st.radio("Aggregation?", ["Total","Mean","Max","Min"])
            time_period = st.radio("Time period?", ["Daily","Weekly","Monthly","Yearly"])
            if st.button("Submit Definition"):
                self.state["intent"].update({
                    "metric_type":metric_type,
                    "filters":filters,
                    "aggregation":aggregation,
                    "time_period":time_period
                })
                st.subheader("Structured KPI Intent")
                st.json(self.state["intent"])
                self.state["step"]=2

        # Step 2: Compute KPI
        if self.state["step"]==2:
            result = self.reference.execute_intent(self.state["intent"])
            st.subheader("Final KPI Result")
            st.json(result)
            return result


# ------------------------------
# Review Card: displays results
# ------------------------------
class ReviewCardGenerator:
    def __init__(self, data_file: str):
        self.agent=KPIAgentHandler(data_file)

    def compute_status_badge(self,kpi_name,value):
        if value is None: return "Critical"
        if "Ratio" in kpi_name:
            return "Good" if value<0.5 else "Warning" if value<1.0 else "Critical"
        if "Count" in kpi_name:
            return "Good" if value==0 else "Warning" if value<5 else "Critical"
        if "Average" in kpi_name or "Hours" in kpi_name:
            return "Good" if value<10 else "Warning" if value<20 else "Critical"
        return "Warning"

    def run_review_card(self):
        st.title("KPI Review Card")
        result=self.agent.run_flow()
        if result and "Error" not in result:
            kpi_name=result.get("KPIName")
            val=result.get("ComputedValue")
            formula=result.get("Formula","N/A")
            unit="events" if result.get("MetricType")=="Count" else "hours" if result.get("MetricType")=="Average" else "ratio"
            badge=self.compute_status_badge(kpi_name,val)
            st.subheader("KPI Review Card")
            st.write(f"**KPI Name:** {kpi_name}")
            st.write(f"**Description:** {result.get('Description','KPI derived from dataset or LLM')}")
            st.write(f"**Formula:** {formula}")
            st.write(f"**Computed Value:** {val}")
            st.write(f"**Unit:** {unit}")
            st.write(f"**Status:** {badge}")
            col1,col2,col3=st.columns(3)
            approve_btn=col1.button("Approve",disabled=(val is None))
            edit_btn=col2.button("Edit")
            regen_btn=col3.button("Regenerate")
            if approve_btn: st.success("KPI Approved.")
            if edit_btn: self.agent.state["step"]=1
            if regen_btn: 
                self.agent.state={"step":0,"intent":{}}
                st.experimental_rerun()
        elif result and "Error" in result:
            st.error(f"KPI validation failed: {result['Error']}")


# ------------------------------
# Example usage with Streamlit
# ------------------------------
if __name__=="__main__":
    review=ReviewCardGenerator("C:\jitendra\JatinKRai-interview\DetectAssignment\KPIAgenticAIBuilder\DataLoader\operations_events.csv")
    review.run_review_card()
