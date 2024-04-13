
1. Install uv package manager
curl -LsSf https://astral.sh/uv/install.sh | sh

2. uv venv  

3. Activate venv
# On macOS and Linux.
source .venv/bin/activate

# On Windows.
.venv\Scripts\activate

4. uv pip install -r requirements.txt

5. flask --app app --debug run

Now app running on port  http://127.0.0.1:8000

Send csv to http://127.0.0.1:5000/upload and it will return json with output prediction:

predictions: predictions
dates: dates 

Test it in http://127.0.0.1:8000:
upload data.csv
freq: D
target_column: values
date_column: date
horizon: 10
predictions returned in json
