from openai import OpenAI, Client
from openai.types.beta.assistant import Assistant
import os
import streamlit as st

client: Client = st.session_state.get(
    "openai_client", OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
)


def get_trained_agent(selected_model: str) -> Assistant:
    file_list = os.listdir(f"training_models/{selected_model}")

    file_list.remove(".gitkeep")

    st.write(f"Files in the {selected_model} dataset:")
    st.write("\n\n".join([f for f in file_list]))

    if st.button("Use this training data"):

        assistant = client.beta.assistants.create(
            instructions="You are a helpful assistant. Use this training data to help answer questions.",
            name=f"{selected_model} assistant",
            model="gpt-4o",
            tools=[{"type": "file_search"}],
        )

        vector_store = client.beta.vector_stores.create(
            name=f"{selected_model} vector store"
        )

        for ff in file_list:
            with open(f"training_models/{selected_model}/{ff}", "rb") as f:
                st.write(f"Uploading {ff}")
                st.write(f"File size: {os.path.getsize(f.name)} bytes")

        file_streams = [
            open(f"training_models/{selected_model}/{f}", "rb") for f in file_list
        ]

        file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
            vector_store_id=vector_store.id, files=file_streams
        )

        assistant = client.beta.assistants.update(
            assistant_id=assistant.id,
            tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
        )

        return assistant


def main():

    st.title("Chatbot")

    if "openai_model" not in st.session_state:
        st.session_state["openai_model"] = "gpt-3.5-turbo"

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    with st.sidebar:
        training_models = os.listdir("training_models")

        training_models.remove(".gitkeep")

        selected_model = st.selectbox(
            "Training data to use", options=[""] + training_models
        )

        if selected_model:
            trained_assistant: Assistant = st.session_state.get(
                "trained_assistant", get_trained_agent(selected_model)
            )

    if not st.session_state.get("trained_assistant", None):
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

            response = client.beta.assistants.message(
                assistant_id=trained_assistant.id,
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
            )

            st.session_state.messages.append({"role": "assistant", "content": response})


if __name__ == "__main__" or __name__ == "__page__":
    main()
