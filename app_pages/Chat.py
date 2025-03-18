from openai import OpenAI, Client, AssistantEventHandler
from openai.types.beta.assistant import Assistant
from openai.types.vector_store import VectorStore
import os
from typing_extensions import override
import streamlit as st
import time

client: Client = st.session_state.get(
    "openai_client", OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
)


class EventHandler(AssistantEventHandler):
    @override
    def on_text_created(self, text) -> None:
        st.session_state.response_text = ""
        print(f"\nassistant > ", end="", flush=True)

    @override
    def on_text_delta(self, delta, snapshot):
        st.session_state.response_text += delta.value
        print(delta.value, end="", flush=True)

    def on_tool_call_created(self, tool_call):
        print(f"\nassistant > {tool_call.type}\n", flush=True)

    def on_tool_call_delta(self, delta, snapshot):
        if delta.type == "code_interpreter":
            if delta.code_interpreter.input:
                print(delta.code_interpreter.input, end="", flush=True)
            if delta.code_interpreter.outputs:
                print(f"\n\noutput >", flush=True)
                for output in delta.code_interpreter.outputs:
                    if output.type == "logs":
                        print(f"\n{output.logs}", flush=True)


def stream_response():
    for word in st.session_state.get("response_text").split(" "):
        yield word + " "
        time.sleep(0.01)

    st.session_state.response_text = ''


def get_trained_agent(selected_model: str) -> Assistant:
    training_option = os.listdir(f"training_models/{selected_model}").pop()

    file_list = os.listdir(f"training_models/{selected_model}/{training_option}")

    st.write(f"Files in the {selected_model} dataset:")
    st.write("\n\n".join([f for f in file_list]))

    if st.button("Use this training data"):

        st.session_state.training_option = training_option

        vector_store = client.vector_stores.create(
            name=f"{selected_model} vector store"
        )

        st.session_state.vector_store = vector_store

        file_streams = [
            open(f"training_models/{selected_model}/{training_option}/{f}", "rb")
            for f in file_list
        ]

        file_batch = client.vector_stores.file_batches.upload_and_poll(
            vector_store_id=vector_store.id, files=file_streams
        )

        if st.session_state.get("training_option", "GUIDED") == "GUIDED":
            instructions = "You are a helpful assistant. Use this training data to help answer questions."
        elif st.session_state.get("training_option") == "EXTRACT":
            instructions = "You are a helpful assistant that only provides answers if the answer is present in the training data. You will cite the training data as much as possible."

        assistant = client.beta.assistants.create(
            instructions=instructions,
            name=f"{selected_model} assistant",
            model="gpt-4o-mini",
            tools=[{"type": "file_search"}],
        )

        assistant = client.beta.assistants.update(
            assistant_id=assistant.id,
            tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
        )

        st.session_state.trained_assistant = assistant


def main():

    st.title("Chatbot")

    if "openai_model" not in st.session_state:
        st.session_state["openai_model"] = "gpt-4o-mini"

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    with st.sidebar:
        training_models = os.listdir("training_models")

        # st.write(st.session_state)

        if ".gitkeep" in training_models:
            training_models.remove(".gitkeep")

        selected_model = st.selectbox(
            "Training data to use", options=[""] + training_models
        )

        if selected_model:
            get_trained_agent(selected_model)
    if not st.session_state.get("training_option", None):
        if prompt := st.chat_input("What is up?"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                stream = client.chat.completions.create(
                    model=st.session_state["openai_model"],
                    messages=[
                        {"role": m["role"], "content": m["content"]}
                        for m in st.session_state.messages
                    ],
                    stream=True,
                )
            response = st.write_stream(stream)
            st.session_state.messages.append({"role": "assistant", "content": response})

    else:
        if prompt := st.chat_input("What is up?"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            trained_assistant: Assistant = st.session_state.get("trained_assistant")

            vector_store: VectorStore = st.session_state.get("vector_store")

            thread = client.beta.threads.create(
                # assistant_id=trained_assistant.id,
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
            )

            print(st.session_state.get("training_option"))

            if st.session_state.get("training_option", "GUIDED") == "GUIDED":
                instructions = "You are a helpful assistant. Use this training data to help answer questions."
            elif st.session_state.get("training_option") == "EXTRACT":
                instructions = "You are a helpful assistant that only provides answers if the answer is present in the training data. You will cite the training data by mentioning which file(s) the information came from. If you do not find the answer in the training data provided, you are allowed to use your existing knowledge base but you must communicate that to the user."

            with st.chat_message("assistant"):
                with client.beta.threads.runs.stream(
                    assistant_id=trained_assistant.id,
                    instructions=instructions,
                    thread_id=thread.id,
                    event_handler=EventHandler(),
                ) as stream:
                    stream.until_done()

            response = st.write_stream(stream_response)
            st.session_state.messages.append({"role": "assistant", "content": response})


if __name__ == "__main__" or __name__ == "__page__":
    main()
