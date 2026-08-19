#KPIInputHandler

import os
from langchain_core.messages import HumanMessage
import inspect
from KPIOperationalEventLoader import KPIOperationalEventLoader

# LangChain + Groq integration
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

# Initialize Groq LLM (make sure GROQ_API_KEY is set in your environment)

os.environ["GROQ_API_KEY"] = ""
groq_llm = ChatGroq(model="llama-3.1-8b-instant")

def groq_llm_response(kpi_name: str) -> str:
    """
    Call Groq LLM using LangChain Core to generate 2-3 lines about KPI Name.
    """
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert KPI analyst. Provide concise explanations."),
        ("human", f"Explain in 2-3 lines what KPI '{kpi_name}' could represent in operational analytics.")
    ])
    chain = prompt | groq_llm
    response = chain.invoke({})
    return response.content


class KPIInputHandler:
    def __init__(self, loader: KPIOperationalEventLoader):
        self.loader = loader

    def handle_input(self, kpi_name: str):
        """
        Check if KPIName exists in KPIOperationalEventLoader.
        If yes, execute and return result.
        If not, call Groq LLM for description.
        """
        methods = {name: func for name, func in inspect.getmembers(self.loader, predicate=inspect.ismethod)}

        if kpi_name in methods:
            try:
                result = methods[kpi_name]()  # Call the KPI method
                return {"KPIName": kpi_name, "Result": result}
            except Exception as e:
                return {"KPIName": kpi_name, "Error": str(e)}
        else:
            description = groq_llm_response(kpi_name)
            return {"KPIName": kpi_name, "Description": description}


# Example usage
if __name__ == "__main__":
    loader = KPIOperationalEventLoader("C:\jitendra\JatinKRai-interview\DetectAssignment\KPIAgenticAIBuilder\DataLoader\operations_events.csv")
    handler = KPIInputHandler(loader)

    print(handler.handle_input("IssueCount"))          # Existing KPI
    print(handler.handle_input("NonExistentKPI"))      # Fallback to Groq
