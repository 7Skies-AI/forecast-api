import pandas as pd


def upload_file(uploaded_file):
    if uploaded_file.filename.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
        return df
    elif uploaded_file.filename.endswith((".xls", ".xlsx")):
        df = pd.read_excel(uploaded_file)
        return df
    elif uploaded_file.filename.endswith(".parquet"):
        df = pd.read_parquet(uploaded_file)
        return df
