import streamlit as st
from google import genai
from dotenv import load_dotenv
import os
from database import getAllStudent_db, search_student_by_id
import json

# 1. Page Setup & API Initialization
st.set_page_config(page_title="Gemini SQL AI Agent", page_icon="🎓")
st.title("🎓 Gemini SQL Database AI Agent")

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    st.error("GOOGLE_API_KEY is not configured in your .env file.")
    st.stop()

client = genai.Client(api_key=api_key)

# 2. Tool Definitions
get_all_students_tool = {
    "type": "function",
    "name": "get_all_students",
    "description": (
        "Retrieves all student records from the students database table. "
        "Use this function when the user asks to see, display, list, "
        "or retrieve all students."
    ),
    "parameters": {
        "type": "object",
        "properties": {},
        "required": []
    }
}

search_student_by_id_tool = {
    "type": "function",
    "name": "search_student_by_id",
    "description": (
        "Searches for a specific student's name and course using their student ID. "
        "Use this function when the user asks about a specific student by ID."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "student_id": {
                "type": "integer",
                "description": "The unique numeric ID of the student to search for."
            }
        },
        "required": ["student_id"]
    }
}

# 3. Agent Logic (Unchanged from terminal version, minus print statements)
def run_agent(user_question):
    interaction = client.interactions.create(
        model="gemini-3.6-flash",
        input=user_question,
        tools=[get_all_students_tool, search_student_by_id_tool]
    )

    function_call = None
    for step in interaction.steps:
        if step.type == "function_call":
            function_call = step
            break

    if function_call is None:
        return interaction.output_text, None

    if function_call.name == "get_all_students":
        records = getAllStudent_db()
        tool_output = [
            {
                "id": row,
                "name": row,
                "course": row,
                "marks": row,
                "city": row
            }
            for row in records
        ]

    elif function_call.name == "search_student_by_id":
        args = function_call.arguments
        if isinstance(args, str):
            args = json.loads(args)
            
        student_id = args.get("student_id")
        record = search_student_by_id(student_id)

        if record:
            tool_output = {
                "id": student_id,
                "name": record,
                "course": record
            }
        else:
            tool_output = {
                "error": f"No student found with ID {student_id}."
            }
    else:
        tool_output = {"error": "Unknown function requested."}

    final_interaction = client.interactions.create(
        model="gemini-3.6-flash",
        previous_interaction_id=interaction.id,
        input=[
            {
                "type": "function_result",
                "name": function_call.name,
                "call_id": function_call.id,
                "result": [
                    {
                        "type": "text",
                        "text": json.dumps(tool_output)
                    }
                ]
            }
        ]
    )

    # Return both the final text and the raw SQL data (optional, for debugging in UI)
    return final_interaction.output_text, {
        "tool": function_call.name,
        "data": tool_output
    }

# 4. Streamlit Chat Interface
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("debug"):
            with st.expander("View SQL Tool Execution"):
                st.write(f"**Tool called:** `{message['debug']['tool']}`")
                st.json(message["debug"]["data"])

# Handle new user input
if prompt := st.chat_input("Ask about students (e.g., 'Who is student 3?' or 'List all students')"):
    # Show user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate and show assistant response
    with st.chat_message("assistant"):
        with st.spinner("Agent is thinking..."):
            try:
                answer, debug_info = run_agent(prompt)
                st.markdown(answer)
                
                if debug_info:
                    with st.expander("View SQL Tool Execution"):
                        st.write(f"**Tool called:** `{debug_info['tool']}`")
                        st.json(debug_info["data"])
                
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "debug": debug_info
                })
            except Exception as error:
                st.error(f"Error: {error}")
