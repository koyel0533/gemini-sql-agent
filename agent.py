from google import genai
from dotenv import load_dotenv,find_dotenv
import os
from database import getAllStudent_db,search_student_by_id
from google.genai import types
import json

load_dotenv()
api_key=os.getenv("GOOGLE_API_KEY")

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY is not configured."
    )
client = genai.Client(api_key=api_key)

get_all_students_tool={
    "type": "function",
    "name": "get_all_students",
    "description": (
        "Retrieves all student records from the "
        "students database table. Uses this function "
        "when the user asks to see, display, list, "
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




def run_agent(user_question):
    print("\n Agent is thinking....")

    result=client.interactions.create(
                model="gemini-3.6-flash",
        input=user_question,
        tools=[get_all_students_tool,search_student_by_id_tool]

    )

    function_call = None
    for step in result.steps:

        if step.type == "function_call":

            function_call = step
            break

    # If Gemini did not request the tool
    if function_call is None:

        return result.output_text

    print("\nGemini selected tool:")
    print(function_call.name)

    print("\nExecuting SQL function...")


    if function_call.name == "get_all_students":

        records = getAllStudent_db()

        # Convert records to JSON-friendly structure
        tool_output = []

        for row in records:

              tool_output.append({
                "id": row[0],
                "name": row[1],
                "course": row[2],
                "marks": row[3],
                "city": row[4]
            })
    elif function_call.name == "search_student_by_id":
        args = function_call.arguments
        if isinstance(args, str):
            args = json.loads(args)
            
        student_id = args.get("student_id")
        record = search_student_by_id(student_id)

        if record:
            tool_output = {
                "id": student_id,
                "name": record[0],
                "course": record[1]
            }
        else:
            tool_output = {
                "error": f"No student found with ID {student_id}."
            }


    else:

         tool_output = {
            "error": "Unknown function requested."
        }

    print("\nSQL result:")
    print(json.dumps(  tool_output, indent=2))

    # ------------------------------------------------
    # Send function result back to Gemini
    # ------------------------------------------------

    final_interaction = client.interactions.create(
        model="gemini-3.6-flash",

        previous_interaction_id=result.id,

        input=[
            {
                "type": "function_result",
                "name": function_call.name,
                "call_id": function_call.id,
                "result": [
                    {
                        "type": "text",
                        "text": json.dumps( tool_output)
                    }
                ]
            }
        ]
    )

    return final_interaction.output_text


# --------------------------------------------------
# 5. Main program
# --------------------------------------------------

print("=" * 60)
print("        GEMINI SQL DATABASE AI AGENT")
print("=" * 60)

print("Type 'exit' to stop.")

while True:

    question = input("\nYou: ")

    if question.lower() == "exit":

        print("Agent: Goodbye!")

        break

    try:

        answer = run_agent(question)

        print("\nAgent:")
        print(answer)

    except Exception as error:

        print("\nError:")
        print(error)
