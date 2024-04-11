import csv

from flask import Flask, jsonify
from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/")
def read_csv():
    try:
        # Replace 'data.csv' with the path to your CSV file
        with open("data.csv", "r") as file:
            csv_reader = csv.reader(file)
            data = [row for row in csv_reader]
        # Returning only the first 5 rows
        return jsonify(data[:5])
    except FileNotFoundError:
        return "CSV file not found."


if __name__ == "__main__":
    app.run(debug=True)
