from openai import OpenAI, Client
from openai.types.beta.assistant import Assistant
import os
import streamlit as st

from shared import extract_training_assistant, create_guided_assistant, guided_training_assistant_chat, TrainingOptions

client: Client = st.session_state.get(
    "openai_client", OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
)


def get_trained_agent(selected_model: str) -> Assistant:
    training_type: str = os.listdir(
        f"training_models/{selected_model}").pop()
    file_list = os.listdir(f"training_models/{selected_model}/{training_type}")

    st.write(f"Files in the {selected_model} dataset:")
    st.write("\n\n".join([f for f in file_list]))

    if st.button("Use this training data"):
        if training_type == TrainingOptions.EXTRACT.name:
            st.session_state.training_option = TrainingOptions.EXTRACT.name
        elif training_type == TrainingOptions.GUIDED.name:
            st.session_state.training_option = TrainingOptions.GUIDED.name
            create_guided_assistant(
                selected_model=selected_model, file_list=file_list)


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

        if ".gitkeep" in training_models:
            training_models.remove(".gitkeep")

        selected_model = st.selectbox(
            "Training data to use", options=[""] + training_models
        )

        if selected_model:
            trained_assistant: Assistant = st.session_state.get(
                "trained_assistant", get_trained_agent(selected_model)
            )
            training_option: str = st.session_state.get("training_option")
    if not st.session_state.get("trained_assistant", None):
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
        if training_option == TrainingOptions.EXTRACT.name:
           st.write("hi")
        elif training_option == TrainingOptions.GUIDED.name:
           guided_training_assistant_chat()


if __name__ == "__main__" or __name__ == "__page__":
    main()
