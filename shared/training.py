from openai import OpenAI, Client
from openai.types.beta.assistant import Assistant
import os
import streamlit as st
from enum import Enum

client: Client = st.session_state.get(
    "openai_client", OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
)


class TrainingOptions(Enum):
    GUIDED = "To help guide the AI to make a decision"
    EXTRACT = "To have AI pull exact information out"


def create_guided_assistant(selected_model: str, file_list: list[str]) -> Assistant:
    assistant = client.beta.assistants.create(
        instructions="You are a helpful assistant. Use this training data to help answer questions.",
        name=f"{selected_model} assistant",
        model="gpt-4o",
        tools=[{"type": "file_search"}],
    )

    vector_store = client.beta.vector_stores.create(
        name=f"{selected_model} vector store"
    )

    st.session_state.vector_store = vector_store

    file_streams = [
        open(f"training_models/{selected_model}/GUIDED/{f}", "rb") for f in file_list
    ]

    file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
        vector_store_id=vector_store.id, files=file_streams
    )

    assistant = client.beta.assistants.update(
        assistant_id=assistant.id,
        tool_resources={"file_search": {
            "vector_store_ids": [vector_store.id]}},
    )

    st.session_state.trained_assistant = assistant

    return assistant


def guided_training_assistant_chat():

    if prompt := st.chat_input("What is up?"):
        st.session_state.messages.append(
            {"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        trained_assistant: Assistant = st.session_state.get(
            "trained_assistant")

        thread = client.beta.threads.create(
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            tool_resources={
                "file_search": {
                    "vector_store_ids": [st.session_state.get("vector_store").id]
                }
            }
        )

        with st.chat_message("assistant"):
            stream = client.beta.threads.runs.stream(
                thread_id=thread.id,
                assistant_id=trained_assistant.id,
                instructions="You are a helpful assistant. Use this training data to help answer questions.",
            )
        response = st.write_stream(stream)
        st.session_state.messages.append(
            {"role": "assistant", "content": response})


def extract_training_assistant(selected_model: str, file_list: list[str]) -> Assistant:
    pass
