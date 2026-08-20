"""
    Agentic KPI Builder: 
    every function is annotated (@tool, @static, @prompt), orchestrated as nodes, 
    and resilient to errors.
    
    Jatin K Rai -- assignment
"""

import inspect
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
import os
import json
from kpi.kpi_loader import KPIOperationalEventLoader
from langchain_core.tools import tool
from dotenv import load_dotenv
from typing import TypedDict, Any
from langchain_core.runnables import RunnablePassthrough, RunnableMap, RunnableLambda

# Define state schema
class KPIState(TypedDict):
    intent: dict   # must be a dict with certain keys
    result: Any
    error: str
    
    
class KPINameReference:
   
    def __init__(self, loader_or_file):
        
        if isinstance(loader_or_file, KPIOperationalEventLoader):
            self.loader = loader_or_file
        else:
            self.loader = KPIOperationalEventLoader(loader_or_file)
        self.df = self.loader.df
        
    
    
    """
    Backend layer: validates KPI intent and executes against dataset.
    If KPI name matches a loader method, executes it.
    Otherwise, calls Groq LLM (or fallback) for description.
    """
    def groq_llm_response(self, kpi_name: str, dataset: Any = None) -> str:
        """
        Produce a short (1-3 sentence) description for the given KPI name based on the provided dataset.
        If dataset is None, uses self.df. The dataset may be a JSON string, a pandas DataFrame-like object
        with to_json, or any JSON-serializable Python structure.
        """
        load_dotenv()
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            return "GROQ_API_KEY not found. Please set it in .env."

        modelname = os.getenv("model")
        if not modelname:
            return "modelname not found. Please set it in .env."

        try:
            groq_llm = ChatGroq(model=modelname)

            # Prepare dataset JSON
            if dataset is None:
                df_json = self.df.to_json(orient="records")
            elif isinstance(dataset, str):
                df_json = dataset
            else:
                try:
                    df_json = dataset.to_json(orient="records")
                except Exception:
                    df_json = json.dumps(dataset)

            # Simple prompt asking the LLM to produce a concise description
            prompt = ChatPromptTemplate.from_messages([
                ("system",
                 "You are a concise assistant that writes short (1-3 sentence) human-readable descriptions of KPIs. "
                 "Given a KPI name and a dataset (as JSON records), produce a brief description of what the KPI measures "
                 "and, at a high level, how it would be computed from the dataset. Output only the description text."),
                ("human", "KPI: {kpi_name}\n\nDataset:\n{data}\n\nPlease provide a concise description.")
            ])

            result = (prompt | groq_llm).invoke({"kpi_name": kpi_name, "data": df_json})

            if isinstance(result, str):
                return result.strip()
            try:
                return str(result)
            except Exception:
                return json.dumps(result)

        except Exception as e:
            return f"Error generating description for KPI '{kpi_name}': {e}"

    def validate_intent(self, intent: dict):
        errors = []
        required_fields = ["kpi_name", "metric_type", "filters", "aggregation", "time_period"]
        for f in required_fields:
            if f not in intent:
                errors.append(f"Missing required field: {f}")
        return errors
    
    # Example node function
    #@tool("validate_intent", description="validate_intent Call")
    def validate_intentagentic(state: KPIState) -> KPIState:
        """
        Validate that the intent dict contains required keys.
        For example, we expect 'query' and 'kpi' keys inside state['intent'].
        """
        intent = state.get("intent", {})
        if not isinstance(intent, dict) or "query" not in intent or "kpi" not in intent:
            # mark error if keys missing
            state["error"] = "Invalid intent: missing 'query' or 'kpi'"
            return state

        # If valid, clear error and continue
        state["error"] = ""
        return state

   
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

        # Fallback: Groq LLM description     
        description = self.groq_llm_response(kpi_name)

        return {
            "KPIName": kpi_name,
            "Description": description
        }
    
    @tool("execute_intent_Agentic", description="execute_intent_Agentic call")
    def execute_intent_Agentic(self, intent):
        errors = self.validate_intent_Agentic(intent)
        if errors:
            return {"Error": errors}

        kpi_name = intent
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

        # Fallback: Groq LLM or mock description     
        description = self.groq_llm_response(kpi_name)

        return {
            "KPIName": kpi_name,
            "Description": description
        }
    
    @tool("validate_intent_Agentic", description="validate_intent_Agentic call")
    def validate_intent_Agentic(self, intent) :
        """
        Validate that the intent dict contains required keys.
        For example, we expect 'query' and 'kpi' keys inside state['intent'].
        """
        errors = []
        
        required_fields = ["kpi_name", "metric_type", "filters", "aggregation", "time_period"]
        for f in required_fields:
            if f == intent:
                errors.append(f"Missing required field: {f}")
        return errors

