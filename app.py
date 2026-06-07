import streamlit as st
from langchain_groq import ChatGroq
from langchain_community.utilities import SQLDatabase
from langchain.chains import create_sql_query_chain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import pandas as pd
import matplotlib.pyplot as plt
import ast
import re
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
groq_api_key = os.getenv("groq")

# Streamlit page configuration
st.set_page_config(page_title="SQL Data Analyst", page_icon="🤖")
st.title("🤖 SQL Data Analyst Assistant")

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,
        input_key="question",
        output_key="answer"
    )

# Sidebar configuration
with st.sidebar:
    st.header("Configuration")
    db_path = st.text_input("Database path", "demodb.db") # C:/Users/Omkar/OneDrive/Desktop/SQL_chat_assistant/demodb.db
    
    if st.button("Initialize System"):
        try:
            # Initialize LLM
            st.session_state.llm = ChatGroq(
                temperature=0,
                groq_api_key=groq_api_key,
                model_name="llama-3.3-70b-versatile"
            )

            # Initialize database
            db_uri = f"sqlite:///{db_path}"
            st.session_state.db = SQLDatabase.from_uri(
                db_uri,
                include_tables=['director_mapping', 'movie', 'ratings', 'genre', 'names', 'role_mapping'],
                sample_rows_in_table_info=3
            )

            # Create chains
            st.session_state.query_chain = create_sql_query_chain(st.session_state.llm, st.session_state.db)
            
            conversation_prompt = PromptTemplate.from_template(
                """You are a helpful SQL data analyst assistant. Use the following context to answer questions.
                
                Previous conversation:
                {chat_history}
                
                Current question: {question}
                
                If this is a follow-up question about previous data analysis, try to answer it using context.
                If it requires new data, say you'll need to run a new query.
                """
            )
            
            st.session_state.conversation_chain = LLMChain(
                llm=st.session_state.llm,
                prompt=conversation_prompt,
                memory=st.session_state.memory,
                output_key="answer"
            )
            
            st.success("System initialized successfully!")
        except Exception as e:
            st.error(f"Initialization failed: {str(e)}")

# Function to try plotting results
def try_plot(result_str, question):
    try:
        # Try converting result string to a list of tuples
        parsed = ast.literal_eval(result_str)

        # If it's a list of tuples, convert to DataFrame
        if isinstance(parsed, list) and all(isinstance(i, (tuple, list)) for i in parsed):
            df = pd.DataFrame(parsed)

            if df.empty:
                return

            # Detect numeric columns
            numeric_cols = df.select_dtypes(include='number').columns.tolist()
            if not numeric_cols:
                return

            # Pick first numeric column to plot
            y_col = numeric_cols[0]
            x_col = df.columns[0] if len(df.columns) > 1 else df.index

            fig, ax = plt.subplots()
            df.plot(kind='bar', x=x_col, y=y_col, legend=False, ax=ax)
            ax.set_title(question)
            ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
            ax.set_ylabel(y_col)
            plt.tight_layout()
            
            # Display plot in Streamlit
            st.pyplot(fig)

    except Exception as e:
        st.warning(f"Could not plot result: {e}")

# Function to execute queries
def execute_query(question):
    try:
        # First check if this is a follow-up that can be answered from memory
        if st.session_state.memory.chat_memory.messages:
            conversation_response = st.session_state.conversation_chain({"question": question})
            if "new query" not in conversation_response["answer"].lower():
                return conversation_response["answer"]

        # Generate SQL query from LLM
        with st.spinner("Generating SQL query..."):
            query_response = st.session_state.query_chain.invoke({"question": question})
        
        # Display SQL query in sidebar
        with st.sidebar:
            st.subheader("Generated SQL Query")
            raw_sql = query_response.split("SQLQuery:")[1].strip()
            cleaned_query = re.sub(r"```sql|```", "", raw_sql).strip()
            st.code(cleaned_query)

        # Check query validity
        if not cleaned_query.lower().startswith(("select", "with")):
            return "❌ Only SELECT queries (or CTEs) are allowed."

        # Run query
        with st.spinner("Executing query..."):
            result = st.session_state.db.run(cleaned_query)
        
        # Display raw results in sidebar
        with st.sidebar:
            st.subheader("Query Results")
            st.text(result)

        # Try to plot results
        try_plot(result, question)

        # Generate summary with follow-up suggestions
        with st.spinner("Analyzing results..."):
            summary_prompt = (
                f"Given the SQL result: {result}\n"
                f"And the question: {question}\n"
                "Give a short, clear, human-readable summary. "
                "Also suggest 2-3 natural follow-up questions that could provide deeper insights."
            )
            summary = st.session_state.llm.invoke(summary_prompt)

        # Store in memory
        st.session_state.memory.save_context(
            {"question": question},
            {"answer": summary.content}
        )
        
        return summary.content

    except Exception as e:
        return f"❌ Error: {str(e)}"

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask your question about the data..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get response
    if "llm" not in st.session_state:
        response = "Please initialize the system in the sidebar first."
    else:
        response = execute_query(prompt)

    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.markdown(response)