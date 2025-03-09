import os
import streamlit as st
from src import convert

model_name = st.text_input("Name your training dataset")
files = st.file_uploader(
    "Upload training documents",
    accept_multiple_files=True,
    type=["txt", "doc", "pdf", "csv"],
)

if files and st.button("Submit data"):
    if len(files) > 5:
        files = files[:5]

        st.warning(
            f"Max of 5 files allowed. Only these files will be used for training data.\n\n {", \n\n".join([x.name for x in files])}"
        )
    os.makedirs("training_models", exist_ok=True)
    for f in files:
        os.makedirs(f"training_models/{model_name}", exist_ok=True)

        file_data, file_name = convert(f)

        with open(f"training_models/{model_name}/{file_name}", "wb") as ff:
            ff.write(file_data)
    st.success("Files saved")
