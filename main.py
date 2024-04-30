from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from utils import interpolate_missing_dates, predict, read_file

app = FastAPI(root_path="/forecast")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/upload/")
async def upload_file(
    file: UploadFile = File(...),
    freq: str = Form(...),
    target_column: str = Form(...),
    date_column: str = Form(...),
    horizon: int = Form(...),
    season_length: int = Form(...),
):
    # try:
    if file.filename == "":
        raise HTTPException(
            status_code=400,
            detail="Unsupported file format. Please upload a CSV or Excel file.",
        )

    df = await read_file(file)
    interpolated_df = interpolate_missing_dates(
        df=df, date_column=date_column, predict_column=target_column, freq=freq
    )
    predict_dict = await predict(
        interpolated_df,
        predict_column=target_column,
        date_column=date_column,
        horizon=horizon,
        season_length=season_length,
    )
    return JSONResponse(content=predict_dict)

    # except Exception as e:
    #    return JSONResponse(content={"error": str(e)})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
