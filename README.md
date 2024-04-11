
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

Now apprunning on port  http://127.0.0.1:5000

