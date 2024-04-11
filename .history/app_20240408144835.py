import csv
import io

from flask import Flask, jsonify, render_template, request
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload_file():
    uploaded_file = request.files["file"]
    if uploaded_file.filename != "":
        # Reading the CSV file
        csv_data = io.StringIO(uploaded_file.stream.read().decode("UTF8"), newline=None)
        csv_reader = csv.reader(csv_data)
        data = [row for row in csv_reader]
        # Returning only the first 5 rows
        return jsonify(data[:5])
    else:
        return "No file selected."


if __name__ == "__main__":
    app.run(debug=True)
