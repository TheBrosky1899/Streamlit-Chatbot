import PyPDF2
from streamlit.runtime.uploaded_file_manager import UploadedFile
from io import StringIO
from typing import Tuple
import pandas as pd


def convert(file: UploadedFile) -> Tuple[bytes, str]:
    file_name: str = file.name

    if file_name.endswith(".pdf"):
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""

        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"

        return text.encode(), file_name.replace(".pdf", ".txt")
    elif file_name.endswith(".txt"):
        return file.read(), file_name
    elif file_name.endswith(".csv"):
        df = pd.read_csv(file)
        return df.to_csv(sep="\t", index=False).encode(), file_name.replace(
            ".csv", ".txt"
        )
