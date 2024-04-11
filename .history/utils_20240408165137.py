import pandas as pd


def upload_file(uploaded_file):
    if uploaded_file.filename != "":
        if uploaded_file.filename.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
            return df
        elif uploaded_file.filename.endswith((".xls", ".xlsx")):
            df = pd.read_excel(uploaded_file)
            return df
        else:
            return "Unsupported file format. Please upload a CSV or Excel file."

    else:
        return "No file selected."
