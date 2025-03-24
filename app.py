import streamlit as st
from langchain.llms import GooglePalm
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAI
from langchain.sql_database import SQLDatabase
from langchain.chains import create_sql_query_chain
import os

# Load environment variables from .env file
load_dotenv()

# Fetch API key from environment variable
google_api = os.getenv("google")
if not google_api:
    st.error("Google API key not found. Please check your .env file.")
    st.stop()

# Initialize the LLM
llm = GoogleGenerativeAI(model="gemini-1.5-pro", google_api_key=google_api)

# Database URI
db_path = "demodb.db"  # Ensure this path is correct
db_uri = f"sqlite:///{db_path}"

# Create SQLDatabase instance with sample rows
db = SQLDatabase.from_uri(
    db_uri,
    include_tables=['Employees', 'Departments'],  # Include your table names
    sample_rows_in_table_info=3
)

# Create SQL query chain
chain = create_sql_query_chain(llm, db)

def execute_query(question):
    try:
        # Generate SQL query
        query = chain.invoke({"question": question})
        print(query)

        # Clean the query (remove ```sql and extra spaces)
        cleaned_query = query.split("SQLQuery:")[1].strip()
        
        # Display the cleaned SQL query in the sidebar
        st.sidebar.write("SQL Query:")
        st.sidebar.code(cleaned_query)
        print(cleaned_query)

        # Normalize the query for validation
        normalized_query = cleaned_query.strip().lower()

        # Check if the query is a SELECT statement or starts with a CTE (WITH)
        if not (
            normalized_query.startswith("select") or
            normalized_query.startswith("with")
        ):
            return "Only SELECT queries (including CTEs) are allowed. This query cannot be executed."

        # Execute the query
        result = db.run(cleaned_query)
        
        # Handle empty results
        if not result:
            return "No results found for your query."

        # Frame a simple short sentence with the result
        finalresult = llm(f"Frame a simple short sentence with the following answer: {result} with reference to the following question: {question}")

        return finalresult

    except Exception as e:
        # Handle invalid queries or execution errors
        error_message = str(e)
        if "no such table" in error_message.lower():
            return "Error: The specified table does not exist."
        elif "no such column" in error_message.lower():
            return "Error: The specified column does not exist."
        elif "syntax error" in error_message.lower():
            return "Error: The generated SQL query is invalid."
        else:
            return f"An error occurred: {error_message}"

# # Streamlit UI
# with st.sidebar:
#     st.write("🔑[Get a Google API key](https://console.cloud.google.com/apis/credentials)")
#     st.write("💻[View the source code](https://github.com/omkarharer/IndiaBudgetRAG-)")

st.title("SQL Assistant 🤖")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "SQL assistant", "content": "How can I help you?"}]

# Display chat messages
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Chat input
if prompt := st.chat_input():
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # Get response from the QA chain
    try:
        response = execute_query(prompt)
        assistant_response = response
    except Exception as e:
        assistant_response = f"Error processing your question: {str(e)}"

    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": assistant_response})
    st.chat_message("assistant").write(assistant_response)