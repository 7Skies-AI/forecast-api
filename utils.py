import io
import re
import time

import pandas as pd

# from statsforecast import StatsForecast
# from statsforecast.models import AutoARIMA
import statsmodels.api as sm
from fastapi import HTTPException


# import pmdarima as pm


async def interpolate_missing_dates(
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

    df = df.drop_duplicates(subset=date_column)
    df = df.set_index(date_column)
    # df = df.interpolate(method="linear")
    # df = df.asfreq(freq, method="ffill")
    df = df.dropna(subset=[predict_column])
    if df[predict_column].dtype == "object":
        df[predict_column] = (
            df[predict_column].astype(str).apply(lambda x: re.sub(r"[^0-9.]", "", x))
        )
        df[predict_column] = df[predict_column].apply(
            lambda x: pd.to_numeric(x, errors="coerce")
        )
        df = df.dropna(subset=[predict_column])
    df = df.reset_index(names=[date_column])
    # df[date_column] = df[date_column]
    # df = df.reset_index(names=[date_column])
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


async def sarimax_forecast(forecasted_df, periods):
    model = sm.tsa.SARIMAX(
        endog=forecasted_df,
        order=(2, 0, 0),
        seasonal_order=(3, 2, 3, 12),  # freq="MS"
    )
    model_fit = model.fit()
    data = model_fit.forecast(steps=periods)

    return data


# async def statsmodels_forecast(forecasted_df, frequency, horizon, season_length):
#    sf = StatsForecast(models=[AutoARIMA(season_length=season_length)], freq=frequency)
#    sf.fit(forecasted_df)
#    predictions_df = sf.predict(h=horizon)
#    predictions = [
#        i for i in predictions_df.reset_index().to_dict()["AutoARIMA"].values()
#    ]
#    dates = [str(i) for i in predictions_df.reset_index().to_dict()["ds"].values()]
#    return {
#        "actual": {
#            "values": forecasted_df["y"].tolist(),
#            "dates": forecasted_df["ds"].tolist(),
#        },
#        "predicted": {"values": predictions, "dates": dates},
#    }


async def predict(
    df, predict_column, date_column="date", horizon=1, freq="M", season_length=12
):
    start = time.time()
    # print(df.head())
    df = df[[predict_column, date_column]]
    df = df.sort_values(by=date_column)
    df = df.set_index(date_column)
    df = df.head(1000)
    df[predict_column] = df[predict_column].astype(float)
    df = df.dropna(subset=[predict_column])
    print(df)
    try:
        predict_data = await sarimax_forecast(forecasted_df=df, periods=horizon)

        print(f"Took {(time.time() - start):.2f} seconds to predict")
        return {
            "actual": {
                "dates": df.index.tolist(),
                "values": df[predict_column].tolist(),
                "predicted": {
                    "dates": predict_data.index.tolist(),
                    "values": predict_data.values.tolist(),
                },
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=404, detail="Data is too small. Try increasing your data size"
        )
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
