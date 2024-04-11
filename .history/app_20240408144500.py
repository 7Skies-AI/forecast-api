import pandas as pd
from flask import Flask, render_template

# Replace 'data.csv' with your actual file name
file_path = "data.csv"

app = Flask(__name__)


@app.route("/")
def get_csv_data():
    try:
        # Read the CSV file using pandas
        df = pd.read_csv(file_path)

        # Get the first 5 rows
        data = df.head(5).to_dict("records")  # Convert to list of dictionaries

        return render_template("data.html", data=data)
    except FileNotFoundError:
        # Handle file not found error
        return "Error: File not found!"


if __name__ == "__main__":
    app.run(debug=True)
