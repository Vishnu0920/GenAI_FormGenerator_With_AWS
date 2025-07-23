import os
import json
import boto3
from aws_config import get_bedrock_client

def get_s3_client():
    return boto3.client(
        's3',
        region_name=os.environ.get('AWS_REGION', 'us-west-2'),
        aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY')
    )

def get_form_list():
    """
    Get list of form schemas from S3 bucket
    """
    s3 = get_s3_client()
    bucket_name = "test-workflow-generation"
    try:
        response = s3.list_objects_v2(Bucket=bucket_name)
        forms = []
        for obj in response.get('Contents', []):
            if obj['Key'].endswith('.json'):
                # Get the form schema
                form_obj = s3.get_object(Bucket=bucket_name, Key=obj['Key'])
                form_data = json.loads(form_obj['Body'].read().decode('utf-8'))
                # Extract form name/label from schema
                form_name = form_data.get('label', '') or form_data.get('title', '') or obj['Key'].replace('.json', '')
                forms.append({
                    'label': form_name,
                    'value': obj['Key']
                })
        return forms
    except Exception as e:
        print(f"Error fetching forms from S3: {str(e)}")
        return []

def get_form_schema(form_key):
    """
    Get specific form schema from S3 bucket
    """
    s3 = get_s3_client()
    bucket_name = "test-workflow-generation"
    try:
        form_obj = s3.get_object(Bucket=bucket_name, Key=form_key)
        form_data = json.loads(form_obj['Body'].read().decode('utf-8'))
        return form_data
    except Exception as e:
        print(f"Error fetching form schema from S3: {str(e)}")
        return None

# Load workflow reference and sample JSONs at module level
WORKFLOW_REFERENCE_DIR = os.path.join(os.path.dirname(__file__), 'workflow_reference')
WORKFLOW_NOTIFICATION_PATH = os.path.join(WORKFLOW_REFERENCE_DIR, 'workflow_notification_sample.json')
WORKFLOW_DATA_ACCESS_PATH = os.path.join(WORKFLOW_REFERENCE_DIR, 'workflow_data_access_sample.json')
WORKFLOW_SYSTEM_PROMPT_PATH = os.path.join(WORKFLOW_REFERENCE_DIR, 'system_prompt.txt')

# Load reference JSONs
with open(WORKFLOW_NOTIFICATION_PATH, 'r', encoding='utf-8') as f:
    NOTIFICATION_REFERENCE = json.load(f)
with open(WORKFLOW_DATA_ACCESS_PATH, 'r', encoding='utf-8') as f:
    DATA_ACCESS_REFERENCE = json.load(f)
with open(WORKFLOW_SYSTEM_PROMPT_PATH, 'r', encoding='utf-8') as f:
    WORKFLOW_SYSTEM_PROMPT = f.read()

def workflow_haiku_handler(prompt, form_key, model_id):
    """
    Generate workflow JSON based on prompt, form schema and references
    """
    # Get form schema
    form_schema = get_form_schema(form_key)
    if not form_schema:
        raise Exception(f"Could not fetch form schema for {form_key}")

    bedrock = get_bedrock_client()
    
    # Prepare context for LLM with form schema and workflow references
    references = {
        "notification_sample": NOTIFICATION_REFERENCE,
        "data_access_sample": DATA_ACCESS_REFERENCE,
        "form_schema": form_schema
    }

    # Combine prompt with context
    combined_message = f"{WORKFLOW_SYSTEM_PROMPT}\n\nForm Schema: {json.dumps(form_schema)}\n\nUser prompt: {prompt}\n\nReference workflow samples: {json.dumps(references)}"

    # Make LLM call
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
