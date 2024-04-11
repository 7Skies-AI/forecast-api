from flask import Flask, jsonify, render_template, request

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload_file():
    uploaded_file = request.files["file"]
    if uploaded_file.filename != "":
        df = upload_file(uploaded_file)
    else:
        return {"error": "Unsupported file format. Please upload a CSV or Excel file."}


if __name__ == "__main__":
    app.run(debug=True)
