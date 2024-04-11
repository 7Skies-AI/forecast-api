from flask import Flask, jsonify, render_template, request

from utils import interpolate_missing_dates, predict, read_file
from utils import interpolate_missing_dates, predict, read_file

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload_file():
    uploaded_file = request.files["file"]
    if uploaded_file.filename != "":
        try:
            freq = request.form["freq"]
            target_column = request.form["target_column"]
            date_column = request.form["date_column"]
            horizon = int(request.form["horizon"])
            df = read_file(uploaded_file)
            interpolated_df = interpolate_missing_dates(
                df=df, date_column=date_column, value_column=target_column, freq=freq
            )
            predict_dict = predict(interpolated_df, horizon, freq=freq)

        except Exception as e:
            return {"error": str(e)}

    else:
        return {"error": "Unsupported file format. Please upload a CSV or Excel file."}


if __name__ == "__main__":
    app.run(debug=True)
