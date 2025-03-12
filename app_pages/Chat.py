from openai import OpenAI, Client
from openai.types.beta.assistant import Assistant
import os
import streamlit as st

client: Client = st.session_state.get(
    "openai_client", OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
)


def get_trained_agent(selected_model: str) -> Assistant:
    training_option = os.listdir(f"training_models/{selected_model}").pop()

    file_list = os.listdir(f"training_models/{selected_model}/{training_option}")

    st.write(f"Files in the {selected_model} dataset:")
    st.write("\n\n".join([f for f in file_list]))

    if st.button("Use this training data"):

        st.session_state.training_option = training_option

        vector_store = client.beta.vector_stores.create(
            name=f"{selected_model} vector store"
        )

        st.session_state.vector_store = vector_store

        file_streams = [
            open(f"training_models/{selected_model}/{training_option}/{f}", "rb") for f in file_list
        ]

        file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
            vector_store_id=vector_store.id, files=file_streams
        )

        if training_option == "GUIDED":

            assistant = client.beta.assistants.create(
                instructions="You are a helpful assistant. Use this training data to help answer questions.",
                name=f"{selected_model} assistant",
                model="gpt-4o",
                tools=[{"type": "file_search"}],
            )

            assistant = client.beta.assistants.update(
                assistant_id=assistant.id,
                tool_resources={"file_search": {
                    "vector_store_ids": [vector_store.id]}},
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

        if ".gitkeep" in training_models:
            training_models.remove(".gitkeep")

        selected_model = st.selectbox(
            "Training data to use", options=[""] + training_models
        )

        if selected_model:
            get_trained_agent(selected_model)
    if not st.session_state.get("training_option", None):
        if prompt := st.chat_input("What is up?"):
            st.session_state.messages.append(
                {"role": "user", "content": prompt})
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
            st.session_state.messages.append(
                {"role": "assistant", "content": response})

    else:
        if st.session_state.get("training_option", "GUIDED") == "GUIDED":
            if prompt := st.chat_input("What is up?"):
                st.session_state.messages.append(
                    {"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)
                trained_assistant: Assistant = st.session_state.get(
                    "trained_assistant")

                thread = client.beta.threads.create(
                    assistant_id=trained_assistant.id,
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
                
        elif st.session_state.get("training_option") == "EXTRACT":
            if prompt := st.chat_input("What is up?"):
                st.session_state.messages.append(
                    {"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)

                with st.chat_message("assistant"):
                    resp = client.files.retrieve()
                    stream = client.chat.completions.create(
                        model=st.session_state["openai_model"],
                        messages=[
                            {"role": m["role"], "content": m["content"]}
                            for m in st.session_state.messages
                        ],
                        stream=True,
                        tools=[{
                            "type": "file_search",
                            "vector_store_ids": [st.session_state.get("vector_store").id]
                        }]
                    )
                response = st.write_stream(stream)
                st.session_state.messages.append(
                    {"role": "assistant", "content": response})


if __name__ == "__main__" or __name__ == "__page__":
    main()
