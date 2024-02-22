import os
import time
import json
import openai
from dotenv import load_dotenv, find_dotenv
import streamlit as st
from openai.types.beta import Assistant
from openai.types.beta.thread import Thread
from openai import OpenAI

load_dotenv(find_dotenv())

client = OpenAI()

assistant = client.beta.assistants.create(
    name="Finance Insight Analyst",
    instructions="You are a helpful financial analyst expert, focusing on management discussions and financial results. Help people learn about financial needs and guide them toward financial literacy.",
    tools=[{"type": "code_interpreter"}, {"type": "retrieval"}],
    model="gpt-3.5-turbo-1106"
)

def show_json(obj):
    print(json.dumps(json.loads(obj.model_dump_json()), indent=4))

show_json(assistant)

def submit_message(assistant_id, thread, user_message):
    message = client.beta.threads.messages.create(
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

def pretty_print(messages):
    responses = [m.content[0].text.value for m in messages if m.role == 'assistant']
    return '\n'.join(responses)

st.set_page_config(
    page_icon="📈",
    page_title="AI Financial Analyst",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.header('Financial AI Analyst')
st.subheader("Ask a financial question and receive tailored advice.")

user_query = st.text_input("Enter your financial query here:", key='user_input', max_chars=250)

if user_query:
    if client:
        with st.spinner('Fetching your financial insights...'):
            thread = client.beta.threads.create()
            run = submit_message(assistant.id, thread, user_query)
            run = wait_on_run(run, thread)
            response_messages = get_response(thread)
            response = pretty_print(response_messages)
            st.write(f'**Response:**\n{response}')