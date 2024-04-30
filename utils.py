import io
import re
import time

import pandas as pd
from statsforecast import StatsForecast
from statsforecast.models import AutoARIMA

# import pmdarima as pm


def interpolate_missing_dates(
    df: pd.DataFrame, date_column: str, predict_column: str, freq="D"
):
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
    df = df.drop_duplicates(subset=date_column)
    df = df.dropna(subset=[predict_column])
    df = df.set_index(date_column).reindex(full_date_range)

    if df[predict_column].dtype == "object":
        df[predict_column] = df[predict_column].apply(
            lambda x: re.sub(r"[^0-9.]", "", x)
        )
        df[predict_column] = df[predict_column].apply(
            lambda x: pd.to_numeric(x, errors="coerce")
        )
        df = df.dropna(subset=[predict_column])

    df[predict_column] = df[predict_column].interpolate(method="linear")

    df = df.reset_index(names=[date_column])
    # df = df.reset_index(drop )  # [[date_column, predict_column]]

    return df


async def read_file(uploaded_file):
    content = await uploaded_file.read()
    if uploaded_file.filename.endswith(".csv"):
        try:  # try to read as utf-8
            df = pd.read_csv(io.StringIO(content.decode("utf-8")))
            return df
        except UnicodeDecodeError:
            # try to read as iso-8859-1
            df = pd.read_csv(io.StringIO(content.decode("iso-8859-1")))
            return df
    elif uploaded_file.filename.endswith((".xls", ".xlsx")):
        df = pd.read_excel(io.BytesIO(content))
        return df
    elif uploaded_file.filename.endswith(".parquet"):
        df = pd.read_parquet(io.BytesIO(content))
        return df


# def sarimax_forecast(forecasted_df, periods):
#    # Forecast
#    n_periods = periods
#    SARIMAX_model = pm.auto_arima(
#        forecasted_df,  # exogenous=df[['month_index']],
#        start_p=1,
#        start_q=1,
#        test="adf",
#        max_p=3,
#        max_q=3,
#        m=12,
#        start_P=0,
#        seasonal=True,
#        d=None,
#        D=1,
#        trace=False,
#        error_action="ignore",
#        suppress_warnings=True,
#        stepwise=True,
#    )
#
#   fitted = SARIMAX_model.predict(
#       n_periods=n_periods,
#       return_conf_int=False,
#   )
#
#   # make series for plotting purpose
#   return {"prediction": fitted.tolist()}


async def statsmodels_forecast(forecasted_df, frequency, horizon, season_length):
    sf = StatsForecast(models=[AutoARIMA(season_length=season_length)], freq=frequency)
    sf.fit(forecasted_df)
    predictions_df = sf.predict(h=horizon)
    predictions = [
        i for i in predictions_df.reset_index().to_dict()["AutoARIMA"].values()
    ]
    dates = [str(i) for i in predictions_df.reset_index().to_dict()["ds"].values()]
    return {"predictions": predictions, "dates": dates}


async def predict(
    df, predict_column, date_column="date", horizon=1, freq="M", season_length=12
):
    start = time.time()
    print(df.head())
    df = df.sort_values(by=date_column)
    df = df.head(1000)
    df = df.dropna(subset=[predict_column])
    df[predict_column] = df[predict_column].astype(float)
    df["unique_id"] = 1
    df = df.rename(columns={date_column: "ds", predict_column: "y"})
    predict_dict = await statsmodels_forecast(
        forecasted_df=df,
        frequency=freq,
        horizon=horizon,
        season_length=season_length,
    )
    print(f"Took {(time.time() - start):.2f} seconds to predict")
    return predict_dict
    # df = df.reset_index(drop=True)
    # df = pd.read_csv("data.csv")
    # last_date = df[date_column].max()
    # new_dates = [
    #    (pd.to_datetime(last_date) + pd.DateOffset(days=i)).strftime("%Y-%m-%d")
    #    for i in range(1, horizon + 1)
    # ]
    # y_hat_dict = sarimax_forecast(df[[predict_column]], horizon)
    # y_hat_dict["dates"] = new_dates  # new_dates
    # return y_hat_dict
