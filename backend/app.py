import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from aws_config import get_bedrock_client
from dotenv import load_dotenv
from typing import Dict

# Load environment variables from .env at the very start
load_dotenv()

app = Flask(__name__)
CORS(app)

# Load field types once at startup
FIELDS_PATH = os.path.join(os.path.dirname(__file__), 'All_Fields.json')
with open(FIELDS_PATH, 'r', encoding='utf-8') as f:
    ALL_FIELDS = json.load(f)

# Load model registry from models.json
MODELS_PATH = os.path.join(os.path.dirname(__file__), 'models.json')
with open(MODELS_PATH, 'r', encoding='utf-8') as f:
    MODELS_LIST = json.load(f)

MODEL_REGISTRY = {}
MODEL_OPTIONS = []
for model in MODELS_LIST:
    model_id = os.environ.get(model["id_env"], model["default_id"]) if model["id_env"] else model["default_id"]
    MODEL_REGISTRY[model["key"]] = {
        "id": model_id,
        "handler": model["handler"]
    }
    MODEL_OPTIONS.append({"label": model["label"], "value": model["key"]})

# System prompt for the LLM
SYSTEM_PROMPT = """
You are an expert form builder. Given a user prompt and a list of possible field types, generate a valid JSON schema for a form that matches the requirements. Only use field types and structure as defined in the provided All_Fields.json. Output only the JSON schema, nothing else.
"""

def claude_haiku_handler(prompt, all_fields, model_id):
    bedrock = get_bedrock_client()
    combined_message = f"{SYSTEM_PROMPT}\n\nUser prompt: {prompt}\n\nAvailable field types: {json.dumps(all_fields)}"
    native_request = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 4096,  # Increased from 1024
        "temperature": 0.2,
        "messages": [
            {"role": "user", "content": [{"type": "text", "text": combined_message}]}
        ]
    }
    request = json.dumps(native_request)
    response = bedrock.invoke_model(modelId=model_id, body=request)
    model_response = json.loads(response["body"].read())
    return model_response["content"][0]["text"].strip()

def deepseek_r1_handler(prompt, all_fields, model_id):
    bedrock = get_bedrock_client()
    combined_prompt = f"{SYSTEM_PROMPT}\n\nUser prompt: {prompt}\n\nAvailable field types: {json.dumps(all_fields)}"
    native_request = {
        "prompt": combined_prompt,
        "temperature": 0.2,
        "top_p": 1.0,
        "max_tokens": 4096,  # Increased from 1024
        "stop": []
    }
    request = json.dumps(native_request)
    response = bedrock.invoke_model(modelId=model_id, body=request)
    model_response = json.loads(response["body"].read())
    return model_response.get("text", "").strip() or model_response.get("content", "").strip()

@app.route('/api/generate-schema', methods=['POST'])
def generate_schema():
    data = request.get_json()
    prompt = data.get('prompt', '').strip()
    model_key = data.get('model', 'claude-3.5-haiku')
    if not prompt:
        return jsonify({'error': 'Prompt is required.'}), 400
    if model_key not in MODEL_REGISTRY:
        return jsonify({'error': f'Unknown model: {model_key}'}), 400
    model_info = MODEL_REGISTRY[model_key]
    handler = globals()[model_info['handler']]
    try:
        schema = handler(prompt, ALL_FIELDS, model_info['id'])
        return schema, 200, {'Content-Type': 'application/json'}
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/models', methods=['GET'])
def get_models():
    return jsonify(MODEL_OPTIONS)

if __name__ == '__main__':
    app.run(debug=True)