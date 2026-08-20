"""
    Agentic KPI Builder: 
    every function is annotated (@tool, @static, @prompt), orchestrated as nodes, 
    and resilient to errors.
    
    Jatin K Rai -- assignment
"""

import os
import streamlit as st
import operator
from typing import TypedDict, Any,Annotated
from langgraph.graph import StateGraph, START, END
from langsmith import Client, trace
from langsmith.run_trees import RunTree  # modern tracing API
from dotenv import load_dotenv
from typing import Optional
from sendgrid.helpers.mail import Mail
from langchain_core.messages import AnyMessage, HumanMessage, SystemMessage, ToolMessage
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

# Import KPI modules
from kpi.kpi_name_reference import KPINameReference
from kpi.tools.kpinamefinder import KPIName_finder


TOOLS_SYSTEM_PROMPT = f"""You are a smart Agentic KPI Builder. Use the tools to look up KPI information.
    could you please provide more information about the KPI builder application for Detect operation event system.
   """
   
# Define state schema for the graph

class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
    

 # Load environment variables
load_dotenv()
langsmith_api_key = os.getenv("LANGSMITH_API_KEY")
os.environ["LANGSMITH_TRACING"] = "true"
if not langsmith_api_key:
    st.error("LANGSMITH_API_KEY not found. Please set it in .env.")


modelname =  os.getenv("model")
if not modelname:
    print("modelname not found. Please set it in .env.")
    

groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    print( "GROQ_API_KEY not found. Please set it in .env.")


#TOOLS = [KPINameReference.execute_intent_Agentic,KPINameReference.validate_intent_Agentic,KPIName_finder]

TOOLS = [KPIName_finder]



class KPIAgenticToolHandler:
    """
    Agentic flow: guides user step by step from KPI name to computed result.
    Tracks conversation state across steps.
    """
    def __init__(self):
        self._tools = {t.name: t for t in TOOLS}
        self._tools_llm =  ChatGroq(model=modelname).bind_tools(TOOLS)
        builder = StateGraph(AgentState)
        builder.add_node('call_tools_llm', self.call_tools_llm)
        builder.add_node('invoke_tools', self.invoke_tools)
        builder.add_node('email_sender', self.email_sender)
        builder.set_entry_point('call_tools_llm')

        builder.add_conditional_edges('call_tools_llm', KPIAgenticToolHandler.exists_action, {'more_tools': 'invoke_tools', 'email_sender': 'email_sender'})
        builder.add_edge('invoke_tools', 'call_tools_llm')
        builder.add_edge('email_sender', END)
        memory = MemorySaver()
        self.graph = builder.compile(checkpointer=memory, interrupt_before=['email_sender'])

        print(self.graph.get_graph().draw_mermaid())

    @staticmethod
    def exists_action(state: AgentState):
        result = state['messages'][-1]
        if len(result.tool_calls) == 0:
            return 'email_sender'
        return 'more_tools'
    
    #Extended for email send
    def email_sender(self, state: AgentState):
        print('Sending email')
        email_llm = ChatGroq(model=modelname,temperature=0.1)
        email_message = [SystemMessage(content=TOOLS_SYSTEM_PROMPT), HumanMessage(content=state['messages'][-1].content)]
        email_response = email_llm.invoke(email_message)
        print('Email content:', email_response.content)

        message = Mail(from_email=os.environ['FROM_EMAIL'], to_emails=os.environ['TO_EMAIL'], subject=os.environ['EMAIL_SUBJECT'],
                       html_content=email_response.content)
        
        print (message)
        """
        try:
          
            sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
            response = sg.send(message)
            print(response.status_code)
            print(response.body)
            print(response.headers)
        except Exception as e:
            print(str(e))
        """
    
    def call_tools_llm(self, state: AgentState):
        try:
            messages = state['messages']
            messages = [SystemMessage(content=TOOLS_SYSTEM_PROMPT)] + messages
            message = self._tools_llm.invoke(messages)
            return {'messages': [message]}
        except Exception as e:
            st.error(f'Error: {e}')

    def invoke_tools(self, state: AgentState):
        try:
            tool_calls = state['messages'][-1].tool_calls
            results = []
            for t in tool_calls:
                print(f'Calling: {t}')
                if not t['name'] in self._tools:  # check for bad tool name from LLM
                    print('\n ....bad tool name....')
                    result = 'bad tool name, retry'  # instruct LLM to retry if bad
                else:
                    print("\n ....t['args']....")
                    print(t['args'])
                    result = self._tools[t['name']].invoke(t['args'])
                results.append(ToolMessage(tool_call_id=t['id'], name=t['name'], content=str(result)))
            print('Back to the model!')
            return {'messages': results}
        except Exception as e:
            st.error(f'Error: {e}')