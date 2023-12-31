import os
import time
import json
import openai
from dotenv import load_dotenv, find_dotenv
import streamlit as st
from openai.types.beta import Assistant
from openai.types.beta.thread import Thread
from openai import OpenAI



st.set_page_config(
    page_icon="📈",
    page_title="AI financial_analyst",
    layout="wide",
    initial_sidebar_state="collapsed",
)

api_key = st.secrets["OPENAI_API_KEY"]

def initialize_openai_client(api_key):    
    return openai.OpenAI(api_key=api_key)



def initialize_openai_client(api_key):    
    return openai.OpenAI(api_key=api_key)

client: openai.OpenAI = openai.OpenAI(api_key=api_key)


assistant: Assistant = client.beta.assistants.create(
    name = "Finance Insight Analyst",
    instructions = "You are a helpful financial analyst expert and, focusing on management discussions and financial results. help people learn about financial needs and guid them towards fincial literacy.",
    tools = [{"type":"code_interpreter"}, {"type": "retrieval"}],
    model = "gpt-3.5-turbo-1106"
)

def show_json(obj):
    print(json.dumps(json.loads(obj.model_dump_json()), indent=4))

show_json(assistant)

def submit_message(assistant_id, thread, user_message):
    client.beta.threads.messages.create(
        thread_id=thread.id, role="user", content=user_message
    )

    return client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant_id,
    )

def wait_on_run(run, thread):
    while run.status == "queued" or run.status == "in_progress":
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id,
        )
        time.sleep(0.5)
    return run

def get_response(thread):
    return client.beta.threads.messages.list(thread_id=thread.id, order="asc")


# Creating a Thread for Conversation
thread: Thread = client.beta.threads.create()

def pretty_print(messages):
    responses = []
    for m in messages:
        if m.role == "assistant":
            responses.append(m.content[0].text.value)
    return "\n".join(responses)



st.sidebar.title("Configuration")
entered_api_key = st.sidebar.text_input("Enter your OpenAI API key", type="password")

client = None


if entered_api_key:
    with st.spinner('Initializing OpenAI Client...'):
        client = initialize_openai_client(entered_api_key)

st.header('Financial Ai Analyst')
st.markdown("""
        Enter your financial question and let our AI empower you with personalized financial strategies for success.
    """)

user_query = st.text_input("Enter your financial query:")

if st.button('Explore Financial Guidance') :
        if  client:
            with st.spinner('Fetching your financial insights...'):
                thread = client.beta.threads.create()
                run = submit_message(assistant.id, thread, user_query)
                run = wait_on_run(run, thread)
                response_messages = get_response(thread)
                response = pretty_print(response_messages)
                st.text_area("Response:", value=response, height=300)
        else:
            st.warning("Kindly input your OpenAi key on the sidebar to unlock access to the application's features")

                
                        
    


