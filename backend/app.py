import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from aws_config import get_bedrock_client
from dotenv import load_dotenv

# Load environment variables from .env at the very start
load_dotenv()

app = Flask(__name__)
CORS(app)

# Load field types once at startup
FIELDS_PATH = os.path.join(os.path.dirname(__file__), 'All_Fields.json')
with open(FIELDS_PATH, 'r', encoding='utf-8') as f:
    ALL_FIELDS = json.load(f)

# System prompt for the LLM
SYSTEM_PROMPT = """
You are an expert form builder. Given a user prompt and a list of possible field types, generate a valid JSON schema for a form that matches the requirements. Only use field types and structure as defined in the provided All_Fields.json. Output only the JSON schema, nothing else.
"""

def generate_schema_with_bedrock(prompt, all_fields):
    bedrock = get_bedrock_client()
    model_id = os.environ.get('BEDROCK_MODEL_ID', 'anthropic.claude-3-haiku-20240307-v1:0')
    # Combine system prompt and user prompt into a single user message
    combined_message = f"{SYSTEM_PROMPT}\n\nUser prompt: {prompt}\n\nAvailable field types: {json.dumps(all_fields)}"
    native_request = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1024,
        "temperature": 0.2,
        "messages": [
            {"role": "user", "content": [{"type": "text", "text": combined_message}]}
        ]
    }
    request = json.dumps(native_request)
    response = bedrock.invoke_model(modelId=model_id, body=request)
    model_response = json.loads(response["body"].read())
    return model_response["content"][0]["text"].strip()

@app.route('/api/generate-schema', methods=['POST'])
def generate_schema():
    data = request.get_json()
    prompt = data.get('prompt', '').strip()
    if not prompt:
        return jsonify({'error': 'Prompt is required.'}), 400
    try:
        schema = generate_schema_with_bedrock(prompt, ALL_FIELDS)
        return schema, 200, {'Content-Type': 'application/json'}
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)