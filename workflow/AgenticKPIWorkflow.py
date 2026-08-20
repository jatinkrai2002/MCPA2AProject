
"""
    Agentic KPI Builder: 
    every function is annotated (@tool, @static, @prompt), orchestrated as nodes, 
    and resilient to errors.
    
    Jatin K Rai -- assignment
"""

"""
Nodes: Each function is registered as a node with graph.add_node.
Edges: Normal progression (entry → validate → execute → review_card) plus error handling (validate_intent → entry, execute_intent → groq_llm_response).
Entry/End: Define where the graph starts and finishes.
Self‑Healing: If validation fails, the graph loops back to entry to re‑ask questions; 
if execution fails, it calls the LLM description node.
"""

from langgraph import Graph
from langgraph import tool, prompt, static

# Import your classes
from kpi.kpi_agent_handler import KPIAgentHandler
from kpi.kpi_name_reference import KPINameReference
from kpi.review_card_generator import ReviewCardGenerator

# Instantiate your objects
agent = KPIAgentHandler("data/operations_events.csv")
reference = KPINameReference("data/operations_events.csv")
review_card = ReviewCardGenerator("data/operations_events.csv")

# Build the graph
graph = Graph(name="AgenticKPIWorkflow")

# Add nodes
graph.add_node("entry", agent.run_flow)
graph.add_node("validate_intent", reference.validate_intent)
graph.add_node("execute_intent", reference.execute_intent)
graph.add_node("groq_llm_response", reference.groq_llm_response)
graph.add_node("review_card", review_card.run_review_card)
graph.add_node("compute_status_badge", review_card.compute_status_badge)

# Wire edges
graph.add_edge("entry", "validate_intent")
graph.add_edge("validate_intent", "execute_intent")
graph.add_edge("validate_intent", "entry", condition="error")   # self-healing loop
graph.add_edge("execute_intent", "review_card")
graph.add_edge("execute_intent", "groq_llm_response", condition="error")
graph.add_edge("groq_llm_response", "review_card")

# Define entry and end
graph.set_entry_point("entry")
graph.set_end_point("review_card")

# Run the graph programmatically
if __name__ == "__main__":
    # This will start at entry, flow through validate → execute → review_card
    result = graph.run()
    print("Workflow finished with result:", result)


    """
    Each node is annotated (@tool, @prompt, @static) so LangGraph can trace and visualize execution.
  The graph supports self‑healing by routing errors back to earlier nodes.
    
    """