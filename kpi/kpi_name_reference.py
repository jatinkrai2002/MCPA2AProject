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
    def groq_llm_response(self, kpi_name: str) -> str:
        """
        Call Groq LLM using LangChain Core to generate 2-3 lines about KPI Name.
        """
        # Load environment variables from .env
        
        load_dotenv()
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            description = "GROQ_API_KEY not found. Please set it in .env."
            return description
        
        modelname =  os.getenv("model")
        if not modelname:
            description = "modelname not found. Please set it in .env."
            return description
        
        try:
            # Otherwise fallback to Groq LLM for description
           
            groq_llm = ChatGroq(model=modelname)
            
            
            # Serialize DataFrame into JSON string (safe for LLMs)
            df_json = self.df.to_json(orient="records")

            # Step 2: Define prompt
            prompt = ChatPromptTemplate.from_messages([
                ("system", 
                """You are an Agentic KPI Builder AI with expertise in Python, LangChain, LangSmith, Langraph, Groq, and DataFrame analytics. 
            Your role is to compute KPI metrics from operational event data.

            Rules:
            - If KPI Name does not exist or is new/custom, ask user for Formula/Logic => Metric Type => Expected Value.
            - For each KPI, return JSON with fields: KPI_Name, Description, Formula, Computed_Value, Unit, Badge.
            - Badge rules: success if matches expected, warning if ±10%, critical if >10% deviation, info if Expected Value = Varies.
            - Always calculate using provided dataset.
            - Output must be a JSON array containing all KPI objects requested.
                """),
                ("human", "{instruction}\n\nDataset:\n{data}")
            ])
            

            # Step 4: Define KPI requests (dicts with string keys!)
            kpi_requests = {
                "Issue Count": {"instruction": "Compute KPI 'Issue Count' from dataset", "data": df_json},
                "Near Miss Count": {"instruction": "Compute KPI 'Near Miss Count' from dataset", "data": df_json},
                "Open Issue Count": {"instruction": "Compute KPI 'Open Issue Count' from dataset", "data": df_json},
                "High Priority Issue Count": {"instruction": "Compute KPI 'High Priority Issue Count' from dataset", "data": df_json},
                "Near Miss to Issue Ratio": {"instruction": "Compute KPI 'Near Miss to Issue Ratio' from dataset", "data": df_json},
                "Average Processing Hours": {"instruction": "Compute KPI 'Average Processing Hours' from dataset", "data": df_json},
                "Total Cost Impact": {"instruction": "Compute KPI 'Total Cost Impact' from dataset", "data": df_json},
                "Critical Issue Count": {"instruction": "Compute KPI 'Critical Issue Count' from dataset", "data": df_json},
                "Avg Customer Impact": {"instruction": "Compute KPI 'Avg Customer Impact' from dataset", "data": df_json},
                "Resolution Rate": {"instruction": "Compute KPI 'Resolution Rate' from dataset", "data": df_json}
            }
            
            # Step 4: Batch KPI instructions into one string
            instruction_text  = """
            Compute the following KPIs from dataset:
            1. Issue Count
            2. Near Miss Count
            3. Resolution Rate
            """
            # Step 5: Invoke once with both variables
            final_output = (prompt | groq_llm).invoke({
                "data": df_json,
                "instruction": instruction_text
            })
            description = final_output

            # Step 5: RunnableMap for parallel KPI calculations
            chain_map = RunnableMap({
                kpi: (prompt | groq_llm)
                for kpi in kpi_requests
            })

            # Step 6: Merge into one JSON array
            merge_chain = chain_map | RunnableLambda(
                lambda results: json.dumps([results[kpi] for kpi in results], indent=2)
            )

            # Step 7: Run
            final_output = merge_chain.invoke(kpi_requests)
           # description = final_output
            print(final_output)

        except Exception as e:
            #self.st.error(f'Error: {e}')
            description = f"KPI '{kpi_name}' is not defined in dataset. It may represent a custom metric.'Error: {e}'"
            
        return description


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

