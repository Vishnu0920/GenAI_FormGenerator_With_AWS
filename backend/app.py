import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from aws_config import get_bedrock_client
from dotenv import load_dotenv

from form_generation import claude_haiku_handler, ALL_FIELDS, FORM_SYSTEM_PROMPT
from workflow_generation import workflow_haiku_handler, get_form_list

# Load environment variables from .env at the very start
load_dotenv()

app = Flask(__name__)
CORS(app)

@app.route('/api/forms', methods=['GET'])
def get_forms():
    try:
        forms = get_form_list()
        return jsonify(forms)
    except Exception as e:
        return jsonify({'error': str(e)}), 500



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




@app.route('/api/generate-workflow', methods=['POST'])
def generate_workflow():
    data = request.get_json()
    prompt = data.get('prompt', '').strip()
    model_key = data.get('model', 'claude-3.5-haiku')
    form_key = data.get('form')

    if not prompt:
        return jsonify({'error': 'Prompt is required.'}), 400
    if not form_key:
        return jsonify({'error': 'Form selection is required.'}), 400
    if model_key not in MODEL_REGISTRY:
        return jsonify({'error': f'Unknown model: {model_key}'}), 400

    model_info = MODEL_REGISTRY[model_key]
    try:
        schema = workflow_haiku_handler(prompt=prompt, form_key=form_key, model_id=model_info['id'])
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
    try:
        schema = claude_haiku_handler(prompt, model_id=model_info['id'])
        return schema, 200, {'Content-Type': 'application/json'}
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/models', methods=['GET'])
def get_models():
    return jsonify(MODEL_OPTIONS)

if __name__ == '__main__':
    app.run(debug=True)