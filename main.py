import streamlit as st
# from langchain.llms import GooglePalm
# from secret import palm
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAI
from langchain.sql_database import SQLDatabase
from langchain.chains import create_sql_query_chain
import os

# Load environment variables from .env file
load_dotenv()

# Fetch API key from environment variable
google_api = os.getenv("google")
# Initialize the LLM
llm = GoogleGenerativeAI(model="gemini-pro", google_api_key=google_api)

# Database URI
db_path =  "demodb.db"     #"C:/Users/Omkar/OneDrive/Desktop/SQL_chat_assistant/demodb.db"
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
        # st.write("\nGenerated SQL Query:")
        # st.code(query)
        print(query)

        # Clean the query (remove ```sql and extra spaces)
        cleaned_query = query.strip('```sql\n').strip('\n```')
        # Display the cleaned SQL query in the sidebar
        st.sidebar.write("SQL Query:")
        st.sidebar.code(cleaned_query)
        print(cleaned_query)

        # Execute the query
        result = db.run(cleaned_query)
        
        # Handle empty results
        if not result:
            return "No results found for your query."

        finalresult=llm("frame simple short sentance with following answer:-" + result + " with refernce to the following question:-" + question)


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

# Streamlit app
st.title("SQL Assistant 🤖")


# Add sidebar options --------------------------------------------------------
# Add sidebar options to show table names (not full schema)
# # Initialize session state for toggle visibility
# if 'show_tables' not in st.session_state:
#     st.session_state.show_tables = False

# # Toggle function
# def toggle_tables():
#     st.session_state.show_tables = not st.session_state.show_tables

# # Add sidebar options
# st.sidebar.title("Options")
# if st.sidebar.button("View Tables", on_click=toggle_tables):
#     pass  # Button click is handled by the toggle function

# # Show/hide tables based on session state
# if st.session_state.show_tables:
#     table_names = db.get_usable_table_names()
#     st.sidebar.write("**Tables in the database:**")
#     st.sidebar.markdown("\n".join([f"- {name}" for name in table_names]))
# else:
#     st.sidebar.write(" ")  # Optional: Add empty space to avoid layout jumps

#---------------------------------------
# Input for user question
question = st.text_input("Enter your question:")

# Add a submit button
if st.button("Submit"):
    if question:
        # Execute the query and display results
        result = execute_query(question)
        st.write("### Query Results:")
        st.write(result)
    else:
        st.warning("Please enter a question before submitting.")
