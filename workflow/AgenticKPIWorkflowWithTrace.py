"""
    Agentic KPI Builder: 
    every function is annotated (@tool, @static, @prompt), orchestrated as nodes, 
    and resilient to errors.
    
    Jatin K Rai -- assignment
"""

from langgraph import Graph
from langsmith import Client
from langsmith import start_trace
import os

#os.environ["LANGSMITH_API_KEY"] = "your_api_key_here"


# Import your KPI classes
from kpi.kpi_agent_handler import KPIAgentHandler
from kpi.kpi_name_reference import KPINameReference
from kpi.review_card_generator import ReviewCardGenerator

# Instantiate objects
agent = KPIAgentHandler("data/operations_events.csv")
reference = KPINameReference("data/operations_events.csv")
review_card = ReviewCardGenerator("data/operations_events.csv")

# Build graph
graph = Graph(name="AgenticKPIWorkflowWithTrace")
graph.add_node("entry", agent.run_flow)
graph.add_node("validate_intent", reference.validate_intent)
graph.add_node("execute_intent", reference.execute_intent)
graph.add_node("groq_llm_response", reference.groq_llm_response)
graph.add_node("review_card", review_card.run_review_card)
graph.add_node("compute_status_badge", review_card.compute_status_badge)

graph.add_edge("entry", "validate_intent")
graph.add_edge("validate_intent", "execute_intent")
graph.add_edge("validate_intent", "entry", condition="error")
graph.add_edge("execute_intent", "review_card")
graph.add_edge("execute_intent", "groq_llm_response", condition="error")
graph.add_edge("groq_llm_response", "review_card")

graph.set_entry_point("entry")
graph.set_end_point("review_card")

# Register with LangSmith
client = Client()  # picks up LANGSMITH_API_KEY from environment
client.create_project(name="AgenticKPIWorkflowWithTrace", description="KPI agentic flow with validation and review card")

# Run with tracing
if __name__ == "__main__":
    with start_trace(project_name="AgenticKPIWorkflowWithTrace") as trace:
        result = graph.run()
        trace.log_output(result)
        print("Workflow finished with result:", result)

"""
Observability: Every KPI run is logged with inputs, outputs, and errors.
Visualization: LangSmith shows the graph execution visually (entry → validate → execute → review card).
Self‑Healing Trace: You can see when validation errors loop back to entry or when execution falls back to LLM.
CI/CD Ready: Combine with pytest to trace test runs automatically.
"""