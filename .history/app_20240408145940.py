import io

import pandas as pd
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload_file():
    uploaded_file = request.files["file"]
    if uploaded_file.filename != "":
        # Check file extension
        if uploaded_file.filename.endswith(".csv"):
            # Read CSV file
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.filename.endswith((".xls", ".xlsx")):
            # Read Excel file
            df = pd.read_excel(uploaded_file)
        else:
            return "Unsupported file format. Please upload a CSV or Excel file."

        # Convert DataFrame to JSON
        json_data = df.head().to_json(orient="records")

        return jsonify(json_data)
    else:
        return "No file selected."


if __name__ == "__main__":
    app.run(debug=True)
