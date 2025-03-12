import os
import streamlit as st

def manage_training_data():
    training_models = os.listdir("training_models")

    if ".gitkeep" in training_models:
        training_models.remove(".gitkeep")

    if selected_model := st.selectbox(
        "Training dataset", options=[""] + training_models
    ):
        if st.button("Delete"):
            import shutil
            try:

                shutil.rmtree(f"training_models/{selected_model}")
                st.success(f"{selected_model} deleted")
            except NotADirectoryError:
                os.remove(f"training_models/{selected_model}")
                st.success(f"{selected_model} deleted")
            except FileNotFoundError:
                st.error(f"{selected_model} not found")

if __name__ == "__main__" or __name__ == "__page__":
    manage_training_data()