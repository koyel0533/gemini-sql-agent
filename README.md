# 🎓 Gemini SQL Database AI Agent

An autonomous **Natural Language-to-SQL (NL-to-SQL) AI Agent** built with **Python**, **Google GenAI SDK**, **SQLite**, and **Streamlit**. Instead of letting an LLM generate and run raw, potentially unsafe SQL queries, this agent uses structured **Function Calling (Tool Use)** with strict JSON schemas and parameterized SQLite queries to safely insert and retrieve student records.

---

## 🎯 Key Perspective & Design Philosophy

Traditional "Text-to-SQL" applications allow an LLM to write raw SQL commands directly—a risky pattern prone to syntax errors, schema hallucinations, and SQL injection attacks.

This project adopts a **Deterministic Tool-Routing Architecture**:
* **Safe, Parameterized Execution:** Gemini never executes raw SQL directly. It acts as an intelligent intent router that extracts structured arguments and maps user prompts to pre-validated Python functions (`add_student` and `search_student_by_id`).
* **Read & Write Capabilities:** Handles both database mutations (`INSERT`) and targeted lookups (`SELECT`) seamlessly through natural language conversation.
* **Transparent Observability:** Includes a collapsible **SQL Tool Execution** drawer under every AI response so users and developers can inspect which database tool was triggered and view the exact JSON payload returned.

---

## 🏗️ System Architecture & Data Pipeline

### Architecture Flow
```text
┌───────────────────┐      1. Natural Language Query       ┌──────────────────────────┐
│   Streamlit UI    │ ───────────────────────────────────► │  Google GenAI Client     │
│    (agent.py)     │                                      │  (gemini-3.6-flash)      │
└─────────▲─────────┘                                      └────────────┬─────────────┘
          │                                                             │
          │ 5. Natural Language Answer                                  │ 2. Tool Selection &
          │    + JSON Debug Drawer                                      │    Extracted Arguments
          │                                                             ▼
┌─────────┴─────────┐      4. Function Result Payload      ┌──────────────────────────┐
│  Session State    │ ◄─────────────────────────────────── │  Python Tool Router      │
│  (Chat History)   │                                      │  (run_agent)             │
└───────────────────┘                                      └────────────┬─────────────┘
                                                                        │
                                                                        │ 3. Parameterized SQL
                                                                        │    (INSERT / SELECT)
                                                                        ▼
                                                           ┌──────────────────────────┐
                                                           │  SQLite3 Database        │
                                                           │  (College.db)            │
                                                           └──────────────────────────┘
```

### Step-by-Step Data Pipeline
1. **Prompt Ingestion:** The user types a request in `agent.py` via `st.chat_input()`, which is saved to `st.session_state.messages` for persistent chat history.
2. **Intent & Parameter Extraction:** `run_agent()` sends the prompt and registered JSON tool schemas (`add_student_tool`, `search_student_by_id_tool`) to `gemini-3.6-flash` via the Interactions API.
3. **Tool Routing:** Python checks `interaction.steps` for a `function_call`, parses the JSON arguments (e.g., `student_id` or new student details), and routes execution to the matching database helper.
4. **Parameterized SQLite Operation:** `database.py` executes parameterized SQL queries (`INSERT INTO Students...` or `SELECT ... WHERE id=?`), commits changes safely, and returns structured JSON results.
5. **Response Synthesis:** The database JSON payload is returned to Gemini using `previous_interaction_id=interaction.id` and `call_id`, enabling the agent to generate a clear, human-readable confirmation or record summary.

---

## 🛠️ Tech Stack

| Layer | Technology | Role |
| :--- | :--- | :--- |
| **Frontend UI** | **Streamlit** | Interactive chat interface (`st.chat_message`), session state memory, and expandable JSON inspection drawers. |
| **AI / LLM Engine** | **Google GenAI SDK** | `gemini-3.6-flash` Interactions API for tool routing, parameter extraction, and response generation. |
| **Database** | **SQLite3** | Lightweight relational database (`College.db`) storing student records. |
| **Backend Logic** | **Python 3.9+** | Tool execution routing, JSON serialization, and database lifecycle management. |
| **Configuration** | **python-dotenv** | Securely loads `GOOGLE_API_KEY` from a local `.env` file. |

---

## 📂 Repository Structure

```text
gemini-sql-database-agent/
│
├── agent.py             # Main Streamlit application & Gemini tool-calling agent
├── database.py          # SQLite3 connection and parameterized CRUD functions
├── College.db           # Relational SQLite database (Students table)
├── .env                 # Environment variables (API keys - excluded from Git)
├── .gitignore           # Ignores .env, venv, and __pycache__
├── requirements.txt     # Python dependencies
└── README.md            # Project documentation
```

---

## ⚙️ Installation & Local Setup

### 1. Clone the Repository
```bash
git clone https://github.com
cd gemini-sql-database-agent
```

### 2. Create & Activate a Virtual Environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install streamlit google-genai python-dotenv
```

### 4. Configure Environment Variables
Create a `.env` file in the root directory and add your Gemini API key:
```env
GOOGLE_API_KEY=your_google_gemini_api_key_here
```

### 5. Run the Application
```bash
streamlit run agent.py
```

---

## 💬 Example Prompts

* **Add a New Student (`INSERT`):**
  > *"Add a new student named Rahul Sharma enrolled in Computer Science with 92 marks from Kolkata."*
* **Fetch One Student (`SELECT`):**
  > *"Find the student with ID 3 and show their course details."*
* **General Greeting (No Tool Triggered):**
  > *"Hi! How can you help me manage the student database?"*

---
## 📸 Demo & Screenshots
<img width="1795" height="881" alt="image" src="https://github.com/user-attachments/assets/2a1af5fe-4073-4854-937a-b091a7643fd2" />
<img width="1852" height="835" alt="image" src="https://github.com/user-attachments/assets/d6cc9d49-e5f0-4005-9230-bbf93798e0e4" />


## 🔮 Future Enhancements

* [ ] **Bulk Retrieval & Filtering:** Add `get_all_students` and `filter_by_course` tools.
* [ ] **Update & Delete Tools:** Support modifying student marks or removing records via natural language.
* [ ] **Multi-Turn Memory:** Carry `previous_interaction_id` across chat messages to handle follow-up questions seamlessly.
* [ ] **Live Sidebar Preview:** Display a real-time `st.dataframe` view of `College.db` in the Streamlit sidebar.

---

## 👨‍💻 Author

**[Koyel Saha]**  
*Aspiring AI / Python Developer*  
 

---

## 📄 License

This project is open-source and available under the [MIT License](LICENSE).
