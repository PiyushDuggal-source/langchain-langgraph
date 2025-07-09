import os
from langchain.agents import create_tool_calling_agent, AgentExecutor
from dotenv import load_dotenv
from langchain.tools import tool

from getpass import getpass

load_dotenv()

os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY") or getpass(
    "Enter GOOGLE_API Key: "
)

gemini_model = "gemini-2.0-flash-lite"


os.environ["TAVILY_API_KEY"] = os.getenv("TAVILY_API_KEY") or getpass(
    "Enter TAVILY_API_KEY Key: "
)

## Search Tool

from langchain_tavily import TavilySearch

search_tool = TavilySearch(max_results=1)

## Custom Tool: get ip

import requests
from datetime import datetime


@tool
def get_location_from_ip():
    """Get the geographical location based on the IP address."""
    try:
        response = requests.get("https://ipinfo.io/json")
        data = response.json()
        if "loc" in data:
            latitude, longitude = data["loc"].split(",")
            data = (
                f"Latitude: {latitude},\n"
                f"Longitude: {longitude},\n"
                f"City: {data.get('city', 'N/A')},\n"
                f"Country: {data.get('country', 'N/A')}"
            )
            return data
        else:
            return "Location could not be determined."
    except Exception as e:
        return f"Error occurred: {e}"


@tool
def get_current_datetime() -> str:
    """Return the current date and time."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


## Creating LLM

from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(model=gemini_model)


## Creating Prompt

from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "you're a helpful assistant"),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ]
)

tools = [search_tool, get_current_datetime, get_location_from_ip]

agent = create_tool_calling_agent(llm=llm, tools=tools, prompt=prompt)

agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

out = agent_executor.invoke(
    {
        "input": (
            "I have a few questions, what is the date and time right now? "
            "How is the weather where I am, get the city info from my IP, Please give me degrees in Celsius "
            "use necessary tools"
        ),
        "agent_scratchpad": [],
    }
)
