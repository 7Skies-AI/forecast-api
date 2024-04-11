import os

import pandas as pd
from statsforecast import StatsForecast
from statsforecast.models import AutoARIMA

os.environ["NIXTLA_ID_AS_COL"] = "1"


def interpolate_missing_dates(df, date_column, predict_column, freq="D"):
    """
    Interpolates missing dates in a DataFrame using linear interpolation.

    Parameters:
    - df: DataFrame containing the data
    - date_column: Name of the column containing dates
    - predict_column: Name of the column containing values to interpolate
    - freq: Frequency for the date range (default is "D" for daily)

    Returns:
    - DataFrame with missing dates interpolated
    """
    if not pd.api.types.is_datetime64_any_dtype(df[date_column]):
        df[date_column] = pd.to_datetime(df[date_column])

    df = df.sort_values(by=date_column)

    full_date_range = pd.date_range(
        start=df[date_column].min(), end=df[date_column].max(), freq=freq
    )

    df = df.set_index(date_column).reindex(full_date_range).reset_index()

    df[predict_column] = df[predict_column].interpolate(method="linear")

    return df


def read_file(uploaded_file):
    if uploaded_file.filename.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
        return df
    elif uploaded_file.filename.endswith((".xls", ".xlsx")):
        df = pd.read_excel(uploaded_file)
        return df
    elif uploaded_file.filename.endswith(".parquet"):
        df = pd.read_parquet(uploaded_file)
        return df


def predict(df, horizon, freq="D"):
    sf = StatsForecast(models=[AutoARIMA(season_length=12)], freq=freq)

    sf.fit(df)
    y_hat_dict = sf.predict(h=horizon, level=[90])
    y_hat_dict["lo-90"] = y_hat_dict["lo-90"].tolist()
    y_hat_dict["hi-90"] = y_hat_dict["hi-90"].tolist()
    y_hat_dict["mean"] = y_hat_dict["mean"].tolist()
    return y_hat_dict
