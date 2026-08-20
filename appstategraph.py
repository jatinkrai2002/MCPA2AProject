"""
    Agentic KPI Builder: 
    every function is annotated (@tool, @static, @prompt), orchestrated as nodes, 
    and resilient to errors.
    
    Jatin K Rai -- assignment
"""

import os
import streamlit as st
import operator
#from langgraph import Graph
from typing import TypedDict, Any,Annotated
from langgraph.graph import StateGraph, START, END
#from langsmith import start_trace
from langsmith import Client, trace
from langsmith.run_trees import RunTree  # modern tracing API
from dotenv import load_dotenv
from typing import Optional
from langchain_core.messages import AnyMessage, HumanMessage, BuilderMessage, ToolMessage
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

# Import KPI modules
from kpi.kpi_agent_handler import KPIAgentHandler
from kpi.kpi_name_reference import KPINameReference
from kpi.review_card_generator import ReviewCardGenerator


TOOLS_Builder_PROMPT = f"""You are a smart Agentic KPI Builder . Use the tools to look up KPI information.
    You are allowed to make multiple calls (either together or in sequence).
    Only look up information when you are sure of what you want.
   """

# Define state schema for the graph

class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
    
"""
class KPIState(TypedDict):
    intent: dict
    result: Any
    error: str
"""
class KPIState(TypedDict, total=False):
    intent: Optional[dict]
    result: Optional[Any]
    error: Optional[str]

def load_css(file_path: str):
    """Utility to load and apply CSS styles."""
    with open(file_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
        
@staticmethod
def exists_action(state: AgentState):
    result = state['messages'][-1]
    if len(result.tool_calls) == 0:
        return 'review_card'
    return 'more_tools'

def call_tools_llm(self, state: AgentState):
    messages = state['messages']
    messages = [BuilderMessage(content=TOOLS_Builder_PROMPT)] + messages
    message = self._tools_llm.invoke(messages)
    return {'messages': [message]}

def invoke_tools(self, state: AgentState):
    tool_calls = state['messages'][-1].tool_calls
    results = []
    for t in tool_calls:
        print(f'Calling: {t}')
        if not t['name'] in self._tools:  # check for bad tool name from LLM
            print('\n ....bad tool name....')
            result = 'bad tool name, retry'  # instruct LLM to retry if bad
        else:
            result = self._tools[t['name']].invoke(t['args'])
        results.append(ToolMessage(tool_call_id=t['id'], name=t['name'], content=str(result)))
    print('Back to the model!')
    return {'messages': results}

def build_graph(data_file: str):
    """Build LangGraph workflow for KPI Builder using StateGraph."""
    
    agent = KPIAgentHandler(data_file)
    reference = KPINameReference(data_file)
    review_card = ReviewCardGenerator(data_file)
    
    modelname =  os.getenv("model")
    if not modelname:
        print("modelname not found. Please set it in .env.")
        return
    
    
    TOOLS = [reference.validate_intent, reference.execute_intent, reference.groq_llm_response, review_card.run_review_card, review_card.compute_status_badge]
    tools_llm =  ChatGroq(model=modelname).bind_tools(TOOLS)
    

    # FIX: StateGraph requires a state schema, not a name
    graph = StateGraph(AgentState)

    # Nodes
    graph.add_node("validate_intent", reference.validate_intent)
    graph.add_node("execute_intent", reference.execute_intent)
    graph.add_node("groq_llm_response", reference.groq_llm_response)
    graph.add_node("review_card", review_card.run_review_card)
    graph.add_node("compute_status_badge", review_card.compute_status_badge)

    # Edges
    graph.add_edge(START, "validate_intent")

    # Branching: decide next node based on state
    def after_validate(state: KPIState):
        if state.get("error"):
            return START   # loop back to entry
        return "execute_intent"

    def after_execute(state: KPIState):
        if state.get("error"):
            return "groq_llm_response"
        return "review_card"

    graph.add_conditional_edges("validate_intent", after_validate)
    graph.add_conditional_edges("execute_intent", after_execute)
    graph.add_edge("groq_llm_response", "review_card")
    graph.add_edge("review_card", END)
    
    memory = MemorySaver()
    graph = graph.compile(name="AgenticKPIWorkflow", checkpointer=memory, interrupt_before=['review_card'])

    print(graph.get_graph().draw_mermaid())

    # FIX: just compile, no end argument
    return graph



def main():
    st.set_page_config(page_title="Agentic KPI Builder", layout="wide")
    load_css("assets/styles.css")

    st.sidebar.title("Agentic KPI Builder")
    st.sidebar.info("Agentic workflow with LangGraph StateGraph + LangSmith tracing.")

    # Load environment variables
    load_dotenv()
    api_key = os.getenv("LANGSMITH_API_KEY")
    os.environ["LANGSMITH_TRACING"] = "true"
    if not api_key:
        st.error("LANGSMITH_API_KEY not found. Please set it in .env.")
        return

    # Build workflow graph
    graph = build_graph("data/operations_events.csv")

    # Register with LangSmith
    client = Client(api_key=api_key)
    
    """
    client.create_project(
        name="AgenticKPIWorkflow",
        description="Agentic KPI flow with validation and review card"
    )
    """
    # Run with tracing
    """
    with start_trace(project_name="AgenticKPIWorkflow", api_key=api_key) as trace:
        # Initial state is empty dict
        result = graph.invoke({"intent": {}, "result": None, "error": ""})
        trace.log_output(result)
        st.success("Workflow finished.")
        st.json(result)
        
    """
    
    # Run with tracing using RunTree
    """
    with RunTree(name="AgenticKPIWorkflow", project_name="AgenticKPIWorkflow") as run:
        result = graph.invoke({"intent": {}, "result": None, "error": ""})
        run.end(output=result)
        st.success("Workflow finished.")
        st.json(result)
    """
    
    
    # Run with tracing: instantiate RunTree directly
    #run = RunTree(name="AgenticKPIWorkflowRun", project_name="AgenticKPIWorkflow")
    
    # Run with a valid initial state
    initial_state = KPIState(
        intent={"query": "Show me KPI trends"},  # or whatever your workflow expects
        result=None,
        error=""
    )

  #  result = graph.invoke(initial_state)

    #result = graph.invoke({"intent": {}, "result": None, "error": ""})
    #run.end(output=result)

    st.success("Workflow finished.")
   # st.json(result)


if __name__ == "__main__":
    main()
