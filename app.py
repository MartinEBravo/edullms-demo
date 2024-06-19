import dotenv
import json
from openai import OpenAI
import streamlit as st

# Load environment variables
dotenv.load_dotenv()

# Initialize OpenAI client
client = OpenAI()

# Load course data
data = json.load(open("courses/iac-1.json"))

# Title of the course
course = data["course"]
# String with the content of the course
content = data["content"]
# List of elements[question, answer] for the course
questions = data["questions"]

def get_context(problem, answer):

    context = f"""
    You are a helpful teacher, you are going to guide the student through doing the proof, here is the question:
    {problem}
    And here is the answer:
    {answer}
    Help the student to understand the proof and guide them to the right direction. Do not give the answer directly.
    """

    return context

def openai_generate_text(context, prompt, conversation):
    """
    Generate text using OpenAI's GPT-3 API
    
    Args:
    context (str): Context for the conversation
    prompt (str): Prompt for the model
    conversation (array): Conversation history

    Returns:
    response (str): Response from the model
    conversation (array): Updated conversation history
    """

    messages = [
        {"role": "system", "content": context},
    ] + conversation

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        stream=True
    )

    response = ""
    message_container = st.chat_message("assistant")
    for chunk in completion:
        if chunk.choices[0].delta.content:
            content = chunk.choices[0].delta.content
            response += content
            yield content

    conversation.append({"role": "assistant", "content": response})


st.title(course)
st.sidebar.title("Materia")
st.sidebar.write(content)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

n = len(questions)
# Select a question from the list
buttons = [f"Problema {i+1}" for i in range(n)]
i = st.selectbox("Selecciona un problema", buttons)

if i:
    i = int(i.split(" ")[1])
    question = questions[i-1]["question"]
    answer = questions[i-1]["answer"]
    st.write(question)

# React to user input
if prompt := st.chat_input("Responde acá..."):

    # Display user message in chat message container
    st.chat_message("user").write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Generate assistant response
    context = get_context(question, answer)
    st.write_stream(openai_generate_text(context, prompt, st.session_state.messages))

