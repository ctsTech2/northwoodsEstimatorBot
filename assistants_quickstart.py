from openai import OpenAI
import shelve
from dotenv import load_dotenv
import os
import time

load_dotenv()
OPEN_AI_API_KEY = os.getenv("OPEN_AI_API_KEY")
client = OpenAI(api_key=OPEN_AI_API_KEY)


# --------------------------------------------------------------
# Upload file
# --------------------------------------------------------------
def upload_file(path):
    # Upload a file with an "assistants" purpose
    file = client.files.create(file=open(path, "rb"), purpose="assistants")
    return file


file = upload_file("./data/foundationTakeoff.pdf")


# --------------------------------------------------------------
# Create assistant
# --------------------------------------------------------------
def create_assistant(file):
    """
    You currently cannot set the temperature for Assistant via the API.
    """
    assistant = client.beta.assistants.create(
        name="Northwoods Estimator Assistant",
        instructions="Objective: Accurately estimate materials for construction projects, with a focus on lumber requirements, adhering to the current Wisconsin Building Code. Data Input: Accept detailed project plans, including dimensions and types of structures. Process lists of required materials (wood types, sizes, treatments). Input current lumber pricing data. Incorporate requirements and specifications from the current Wisconsin Building Code. Calculations: Calculate total lumber quantities considering standard sizes and lengths. Apply a waste factor for cuts and errors, in compliance with building code standards. Estimate costs by multiplying material quantities with current prices. Offer alternative material options for cost efficiency, ensuring they meet building code requirements. Reporting: Generate a detailed report listing materials, quantities, costs, and building code compliance aspects. Provide a summary overview of total costs, potential savings, and building code considerations. Allow for the export of reports in various formats (e.g., PDF, Excel). Updates and Adjustments: Enable updates to project specifications and re-estimation, including changes in building code regulations. Regularly update material prices and building code information for accurate estimations. User Interface: Develop an intuitive interface for easy input of project details and building code requirements. Include a help and guidance section, with references to building code specifics. Additional Features: Utilize historical project data to refine estimates, with a focus on building code compliance trends. Integrate with lumberyard inventory systems, if available, for real-time stock and building code adherence. When asking for information to complete the task, please be concise, number each item you need from the user, and ask for no more than 3 items at a time.",
        tools=[{"type": "retrieval"}],
        model="gpt-4-1106-preview",
        file_ids=[file.id],
    )
    return assistant


assistant = create_assistant(file)


# --------------------------------------------------------------
# Thread management
# --------------------------------------------------------------
def check_if_thread_exists(cust_id):
    with shelve.open("threads_db") as threads_shelf:
        return threads_shelf.get(cust_id, None)


def store_thread(cust_id, thread_id):
    with shelve.open("threads_db", writeback=True) as threads_shelf:
        threads_shelf[cust_id] = thread_id

# def generate_response(message_body):
#     thread = client.beta.threads.create()
#     thread_id = thread.id

#     message = client.beta.threads.messages.create(
#         thread_id=thread_id,
#         role="user",
#         content=message_body,
#     )
    
#     message_body = "I'd like to get a quote for a 12x12 deck."



# --------------------------------------------------------------
# Generate response
# --------------------------------------------------------------
def generate_response(message_body, cust_id, name):
    # Check if there is already a thread_id for the cust_id
    thread_id = check_if_thread_exists(cust_id)

    # If a thread doesn't exist, create one and store it
    # if thread_id is None:
    #     print(f"Creating new thread for {name} with cust_id {cust_id}")
    #     thread = client.beta.threads.create()
    #     store_thread(cust_id, thread.id)
    #     thread_id = thread.id

    # # Otherwise, retrieve the existing thread
    # else:
    #     print(f"Retrieving existing thread for {name} with cust_id {cust_id}")
    #     thread = client.beta.threads.retrieve(thread_id)

    # # Add message to thread
    # message = client.beta.threads.messages.create(
    #     thread_id=thread_id,
    #     role="user",
    #     content=message_body,
    # )

    # # Run the assistant and get the new message
    # new_message = run_assistant(thread)
    # print(f"To {name}:", new_message)
    # return new_message


# # --------------------------------------------------------------
# # Run assistant
# # --------------------------------------------------------------
def run_assistant():
    # Retrieve the Assistant
    assistant = client.beta.assistants.retrieve("asst_bBnWdU3NCVf7lhZU27m1gwp1")
    thread = client.beta.threads.retrieve("thread_ofejyOhWqHPM5aIeCYlSmo0p")
    

#     # Run the assistant
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id,
    )

#     # Wait for completion
    while run.status != "completed":
        # Be nice to the API
        time.sleep(0.5)
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

#     # Retrieve the Messages
    messages = client.beta.threads.messages.list(thread_id=thread.id)
    new_message = messages.data[0].content[0].text.value
    print(f"Generated message: {new_message}")
    return new_message


# # --------------------------------------------------------------
# # Test assistant
# # --------------------------------------------------------------

# new_message = generate_response("What's the check in time?", "123", "John")

# new_message = generate_response("What's the pin for the lockbox?", "456", "Sarah")

# new_message = generate_response("What was my previous question?", "123", "John")

# new_message = generate_response("What was my previous question?", "456", "Sarah")
