import os
from typing import Optional
from dotenv import load_dotenv
from serpapi import GoogleSearch
from pydantic import BaseModel, Field
from langchain_core.tools import tool

load_dotenv()
serp_api_key = os.getenv("SERPAPI_API_KEY")
if not serp_api_key:
    print( "SERPAPI_API_KEY not found. Please set it in .env.")

class KPINameInput(BaseModel):
    kpiName: Optional[str] = Field(description='KPIName value used by input')


class KPINameInputSchema(BaseModel):
    params: KPINameInput


@tool(args_schema=KPINameInputSchema)
def KPIName_finder(params: KPINameInput):
    '''
    Find KPI Name using Goodle Search.

    Returns:
        dict: KPI Name search results.
    '''
    params = {
    "engine": "google",      # Specify the search engine
    "q": params.kpiName,           # Your search query
    "location": "India",# Optional: Location-based search
    "hl": "en",              # Optional: Language
    "gl": "us",              # Optional: Country
    "api_key": serp_api_key 
    }
    
    try:
        search = GoogleSearch(params)
        results = search.get_dict()

        # Access organic search results
       #  organic_results = results.get("organic_results", [])
    
    except Exception as e:
        results = str(e)
        
    return results
"""
for result in organic_results:
    print(f"Title: {result.get('title')}")
    print(f"Link: {result.get('link')}\n")
"""