from openai import OpenAI
import os
import streamlit as st

def main():

    st.title("Chatbot Wrapper")

    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

    if "openai_model" not in st.session_state:
        st.session_state["openai_model"] = "gpt-3.5-turbo"

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    with st.sidebar:
        training_models = os.listdir('training_models')

        selected_model = st.selectbox("Training data to use", options=[""] + training_models)

        if selected_model:
            file_list = os.listdir(f"training_models/{selected_model}")

            st.write(f"Files in the {selected_model} dataset:")
            st.write("\n\n".join([f for f in file_list]))

            # TODO: https://stackoverflow.com/questions/78084538/openai-assistants-api-how-do-i-upload-a-file-and-use-it-as-a-knowledge-base
            if st.button("Use this training data"):
                for file in file_list:
                    with open(f"training_models/{selected_model}/{file}") as f:
                        client.files.create(
                            file=f,
                            purpose="assistants"
                        )
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

if __name__ == "__main__" or __name__ == "__page__":
    main()