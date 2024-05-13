from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from utils import interpolate_missing_dates, predict, read_file

app = FastAPI(root_path="/forecast")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,  # Set to True if API allows cookies
    allow_methods=["*"],  # List of allowed HTTP methods (or "*" for all)
    allow_headers=["*"],  # List of allowed headers (or "*" for all)
)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/upload/")
async def upload_file(
    file: UploadFile = File(...),
    target_column: str = Form(...),
    date_column: str = Form(...),
    horizon: int = Form(...),
    # season_length: int = Form(...),
):
    """
    Uploads a file and performs time series forecasting using the provided parameters.

    Parameters:
        file (UploadFile): The file to be uploaded.
        freq (str): The frequency of the time series data. "D" for daily, "M" for monthly, "Y" for yearly.
        target_column (str): The name of the target column in the file.
        date_column (str): The name of the date column in the file.
        horizon (int): The number of time steps to forecast into the future.

    Returns:
        dict: A dictionary containing the predicted values and corresponding dates.

    Raises:
        HTTPException: If the file format is unsupported.

    """
    # try:
    # if freq.lower() == "d":
    #    season_length = 365
    # elif freq.lower() == "m":
    #    season_length = 12
    # elif freq.lower() == "y":
    #    season_length = 1
    # else:
    #    raise HTTPException(
    #        status_code=400,
    #        detail="Invalid frequency. Please use 'D' for daily, 'M' for monthly, or 'Y' for yearly.",
    #    )
    if file.filename == "":
        raise HTTPException(
            status_code=400,
            detail="Unsupported file format. Please upload a CSV or Excel file.",
        )

    df = await read_file(file)
    interpolated_df = await interpolate_missing_dates(
        df=df,
        date_column=date_column,
        predict_column=target_column,  # freq=freq
    )
    predict_dict = await predict(
        interpolated_df,
        predict_column=target_column,
        date_column=date_column,
        horizon=horizon,
        #   freq=freq,
        #   season_length=season_length,
    )

    # predict_dict["actual"] = {
    #    "values": df[target_column].tolist(),
    #    "dates": df[date_column].astype(str).tolist(),
    # }
    return predict_dict
    # except Exception as e:
    #    return JSONResponse(content={"error": str(e)})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
