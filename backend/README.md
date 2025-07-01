# Backend (Flask + AWS Bedrock)

## Setup

1. Create and activate a virtual environment:
   ```sh
   python -m venv venv
   venv\Scripts\activate  # On Windows
   # source venv/bin/activate  # On Mac/Linux
   ```
2. Install dependencies:
   ```sh
   pip install flask boto3 flask-cors
   ```
3. Place your `All_Fields.json` in this directory (already present).

## AWS Credentials
- Set the following environment variables (in your shell or a `.env` file):
  - `AWS_ACCESS_KEY_ID`
  - `AWS_SECRET_ACCESS_KEY`
  - `AWS_SESSION_TOKEN` (if needed)
  - `AWS_REGION` (default: `us-east-1`)
  - `BEDROCK_MODEL_ID` (default: `anthropic.claude-v2`)

## Running
```sh
flask run
```

The API will be available at `http://localhost:5000/api/generate-schema`. 