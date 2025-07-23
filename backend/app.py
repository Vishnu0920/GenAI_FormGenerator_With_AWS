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


# Form reference fields and system prompt
FORM_REFERENCE_DIR = os.path.join(os.path.dirname(__file__), 'form_reference')
FORM_REFERENCE_PATH = os.path.join(FORM_REFERENCE_DIR, 'All_Fields.json')
FORM_SYSTEM_PROMPT_PATH = os.path.join(FORM_REFERENCE_DIR, 'system_prompt.txt')
with open(FORM_REFERENCE_PATH, 'r', encoding='utf-8') as f:
    ALL_FIELDS = json.load(f)
with open(FORM_SYSTEM_PROMPT_PATH, 'r', encoding='utf-8') as f:
    FORM_SYSTEM_PROMPT = f.read()

# Workflow reference fields and system prompt (placeholder, update as needed)
WORKFLOW_REFERENCE_DIR = os.path.join(os.path.dirname(__file__), 'workflow_reference')
WORKFLOW_REFERENCE_PATH = os.path.join(WORKFLOW_REFERENCE_DIR, 'workflow_reference.json')
WORKFLOW_SYSTEM_PROMPT_PATH = os.path.join(WORKFLOW_REFERENCE_DIR, 'system_prompt.txt')
if os.path.exists(WORKFLOW_REFERENCE_PATH):
    with open(WORKFLOW_REFERENCE_PATH, 'r', encoding='utf-8') as f:
        WORKFLOW_REFERENCE = json.load(f)
else:
    WORKFLOW_REFERENCE = {}  # Empty until you add a schema
if os.path.exists(WORKFLOW_SYSTEM_PROMPT_PATH):
    with open(WORKFLOW_SYSTEM_PROMPT_PATH, 'r', encoding='utf-8') as f:
        WORKFLOW_SYSTEM_PROMPT = f.read()
else:
    WORKFLOW_SYSTEM_PROMPT = "You are an expert workflow generator. Given a user prompt and a reference workflow schema, generate a valid workflow JSON."

# Load model registry from models.json
MODELS_PATH = os.path.join(os.path.dirname(__file__), 'models.json')
with open(MODELS_PATH, 'r', encoding='utf-8') as f:
    MODELS_LIST = json.load(f)

# Remove Deepseek from model registry setup
MODEL_REGISTRY = {}
MODEL_OPTIONS = []
for model in MODELS_LIST:
    model_id = os.environ.get(model["id_env"], model["default_id"]) if model["id_env"] else model["default_id"]
    MODEL_REGISTRY[model["key"]] = {
        "id": model_id,
        "handler": model["handler"]
    }
    MODEL_OPTIONS.append({"label": model["label"], "value": model["key"]})


# Handler for form generation

# Handler for form generation
def claude_haiku_handler(prompt, all_fields, model_id):
    bedrock = get_bedrock_client()
    combined_message = f"{FORM_SYSTEM_PROMPT}\n\nUser prompt: {prompt}\n\nAvailable field types: {json.dumps(all_fields)}"
    native_request = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 4096,
        "temperature": 1,
        "messages": [
            {"role": "user", "content": [{"type": "text", "text": combined_message}]}
        ]
    }
    request = json.dumps(native_request)
    response = bedrock.invoke_model(modelId=model_id, body=request)
    model_response = json.loads(response["body"].read())
    return model_response["content"][0]["text"].strip()

# Handler for workflow generation (update logic as needed)

# Handler for workflow generation
def workflow_haiku_handler(prompt, workflow_reference, model_id):
    bedrock = get_bedrock_client()
    combined_message = f"{WORKFLOW_SYSTEM_PROMPT}\n\nUser prompt: {prompt}\n\nReference workflow schema: {json.dumps(workflow_reference)}"
    native_request = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 4096,
        "temperature": 1,
        "messages": [
            {"role": "user", "content": [{"type": "text", "text": combined_message}]}
        ]
    }
    request = json.dumps(native_request)
    response = bedrock.invoke_model(modelId=model_id, body=request)
    model_response = json.loads(response["body"].read())
    return model_response["content"][0]["text"].strip()
@app.route('/api/generate-workflow', methods=['POST'])
def generate_workflow():
    data = request.get_json()
    prompt = data.get('prompt', '').strip()
    model_key = data.get('model', 'claude-3.5-haiku')
    if not prompt:
        return jsonify({'error': 'Prompt is required.'}), 400
    if model_key not in MODEL_REGISTRY:
        return jsonify({'error': f'Unknown model: {model_key}'}), 400
    model_info = MODEL_REGISTRY[model_key]
    try:
        # Use workflow handler and reference
        schema = workflow_haiku_handler(prompt, WORKFLOW_REFERENCE, model_info['id'])
        return schema, 200, {'Content-Type': 'application/json'}
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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