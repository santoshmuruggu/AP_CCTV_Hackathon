# query_agent.py

import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from langchain_community.chat_models import ChatOpenAI
from langchain.agents import create_sql_agent
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.sql_database import SQLDatabase

# Load OpenAI API key from .env
load_dotenv()
openai_key = os.getenv("OPENAI_API_KEY")

# Setup SQLAlchemy DB engine
engine = create_engine("sqlite:///./database.db")
db = SQLDatabase(engine)

# Setup OpenAI + LangChain agent
llm = ChatOpenAI(temperature=0, openai_api_key=openai_key, model="gpt-3.5-turbo")
toolkit = SQLDatabaseToolkit(db=db, llm=llm)
agent_executor = create_sql_agent(llm=llm, toolkit=toolkit, verbose=True)

def ask_sql_agent(question: str):
    try:
        result = agent_executor.invoke({"input": question}, handle_parsing_errors=True)
        print("Generated SQL:\n", result.get("intermediate_steps", "N/A"))
        return result["output"]
    except Exception as e:
        return f"❌ GPT/SQL Error: {str(e)}"


