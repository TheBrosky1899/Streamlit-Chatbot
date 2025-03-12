import os
import streamlit as st
from shared import TrainingOptions

model_name = st.text_input("Name your training dataset")
files = st.file_uploader(
    "Upload training documents",
    accept_multiple_files=True,
    type=['c', 'cpp', 'cs', 'css', 'doc', 'docx', 'go', 'html', 'java', 'js',
          'json', 'md', 'pdf', 'php', 'pptx', 'py', 'rb', 'sh', 'tex', 'ts', 'txt'],
)



training_option = st.selectbox("How should the training data be used?", options=[
                               ""] + [x.value for x in TrainingOptions])

if training_option == TrainingOptions.GUIDED.value:
    st.code(f"""
        Example:
                
            You upload a file about dogs. 
                
            The chatbot will use this data alongside existing information to dermine it's response.
    """, language="text")
elif training_option == TrainingOptions.EXTRACT.value:
    st.code(f"""
        Example:
                
            You upload a file about dogs. 
                
            The chatbot will use this data in favor of existing information and can pull quotations out of the dataset.
    """, language="text")

if model_name and files and training_option and st.button("Submit data"):
    if len(files) > 5:
        files = files[:5]

        short_file_list = ', \n\n'.join([x.name for x in files])

        st.warning(
            f"""Max of 5 files allowed. Only these files will be used for training data. {short_file_list}"""
        )
    os.makedirs("training_models", exist_ok=True)
    for f in files:
        os.makedirs(f"training_models/{model_name}/{TrainingOptions(training_option).name}", exist_ok=True)

        with open(f"training_models/{model_name}/{TrainingOptions(training_option).name}/{f.name}", "wb") as ff:
            ff.write(f.read())
    st.success("Files saved")