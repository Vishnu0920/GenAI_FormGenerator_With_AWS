import os
import json
from aws_config import get_bedrock_client

# Load form reference and system prompt at module level
FORM_REFERENCE_DIR = os.path.join(os.path.dirname(__file__), 'form_reference')
FORM_REFERENCE_PATH = os.path.join(FORM_REFERENCE_DIR, 'All_Fields.json')
FORM_SYSTEM_PROMPT_PATH = os.path.join(FORM_REFERENCE_DIR, 'system_prompt.txt')
with open(FORM_REFERENCE_PATH, 'r', encoding='utf-8') as f:
    ALL_FIELDS = json.load(f)
with open(FORM_SYSTEM_PROMPT_PATH, 'r', encoding='utf-8') as f:
    FORM_SYSTEM_PROMPT = f.read()

def claude_haiku_handler(prompt, all_fields=None, model_id=None, form_system_prompt=None):
    bedrock = get_bedrock_client()
    # Use defaults if not provided
    if all_fields is None:
        all_fields = ALL_FIELDS
    if form_system_prompt is None:
        form_system_prompt = FORM_SYSTEM_PROMPT
    combined_message = f"{form_system_prompt}\n\nUser prompt: {prompt}\n\nAvailable field types: {json.dumps(all_fields)}"
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
