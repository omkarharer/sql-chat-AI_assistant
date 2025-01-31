
# SQL Chat Assistant 🤖

The SQL Chat Assistant is a Streamlit-based web application that allows users to interact with a SQL database using natural language. It uses a Language Learning Model (LLM) to generate SQL queries from user questions, executes them on a SQLite database, and provides the results in a user-friendly format. Checkout the demo using following URL=
https://sql-chat-aiassistant-omkarharer.streamlit.app/

## How It Works

User Input: The user enters a natural language question (e.g., "Who is the manager of the Sales department?").

Query Generation: The app uses an LLM (e.g., Groq or Google Generative AI) to generate a SQL query from the question.

Query Execution: The generated SQL query is executed on a SQLite database.

Result Formatting: The app formats the query results into a natural language response and displays it to the user.


```bash

       +-------------------+
       |   User Interface  |   <-- User Input (Natural Language)
       +-------------------+
               |
               v
       +---------------------------+
       |   LLM (ChatGroq/Gemini)   |   <-- Converts Query to SQL
       +---------------------------+
               |
               v
       +--------------------------+
       |  SQL Query Generation   |   <-- Formats SQL Query
       +--------------------------+
               |
               v
       +-------------------+
       |   SQL Database    |   <-- Executes SQL Query
       +-------------------+
               |
               v
       +--------------------------+
       |   Response Generation    |   <-- Converts Data to Natural Language
       +--------------------------+
               |
               v
       +-------------------+
       |   User Interface  |   <-- Displays Answer
       +-------------------+


```

# 🚀 Steps to Run the SQL Chat Assistant Locally

1️⃣ Clone the GitHub Repository

Open your terminal or command prompt and run:
   ```commandline
   git clone <repo-url>
   cd <your-repo-folder>
   ```



2️⃣ Create and Activate a Virtual Environment

Using Conda:
   ```commandline
   conda create -n sqlbot python=3.12 -y
conda activate sqlbot
   ```
Or using virtualenv (alternative to Conda):
   ```commandline
python -m venv sqlbot
source sqlbot/bin/activate  # On macOS/Linux
sqlbot\Scripts\activate     # On Windows

   ```

3️⃣ Install Required Dependencies

   ```commandline
pip install -r requirements.txt

   ```

4️⃣ Get API Key for LLM

- Obtain your API key from **Google AI Studio** using the link below:  
  - 🔗 [Get Your Google AI Studio API Key](https://aistudio.google.com/app/apikey)  
Create a .env file in the project directory and add your API key:

   ```commandline
GOOGLE_API_KEY=your_google_api_key_here
   ```

6️⃣ Run the Streamlit App
  ```commandline
streamlit run app.py
   ```


# 🚀Deployment to Streamlit Community Cloud

Push your code to GitHub.

Deploy the app to Streamlit Community Cloud.

Add your API key to Streamlit’s Secrets:
   ```commandline
GOOGLE_API_KEY=your_google_api_key_here
   ```
   Share the public URL (e.g., https://sql-chat-aiassistant-omkarharer.streamlit.app/) with others.


## Known Limitations

### Database Dependency
- The app currently works only with **SQLite** databases.  
- Support for other databases (e.g., **PostgreSQL**, **MySQL**) can be added in future versions.

### LLM Limitations
- The accuracy of generated SQL queries depends on the **LLM’s capabilities**.  
- Complex queries may not always generate correct SQL statements.

### Error Handling
- The app handles common errors (e.g., **missing tables, invalid queries**).  
- Some **edge cases** may not be fully covered.

### Scalability
- Designed for **small to medium-sized datasets**.  
- For **large datasets**, consider using a **cloud-based database**.

---

## Suggestions for Improvement

### 🚀 Few-Shot Learning for Complex Queries
- Implement **few-shot learning** to improve handling of complex SQL queries.  
- Provide examples of **complex queries and their corresponding SQL statements** to guide the model.

### 🎤 Audio-to-Text & Text-to-Audio
- Support for **voice input (audio-to-text)** and **voice output (text-to-audio)** to enhance user interaction.

### 🗄️ Support for Multiple Databases
- Extend support to **PostgreSQL, MySQL, MongoDB**, and other database systems.


### 🔐 User Authentication
- Implement **authentication** to **restrict access** and enhance security.


### 🖥️ UI Improvements
- Add a **history of previous queries and results** for a better user experience.
