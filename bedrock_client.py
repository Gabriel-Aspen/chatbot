import os
import boto3
import json

AWS_REGION = os.getenv("AWS_REGION", "us-west-2")

# Create a boto3 client for Bedrock
bedrock = boto3.client(
    "bedrock-runtime",
    region_name=AWS_REGION,
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
)

# Claude 3 Sonnet model ID for Bedrock
CLAUDE_MODEL_ID = "us.anthropic.claude-3-7-sonnet-20250219-v1:0"

def invoke_claude(messages):
    """
    Invokes the Claude 3 model on AWS Bedrock with the given messages.
    messages: list of dicts with 'role' and 'content' keys (like OpenAI format)
    Returns the assistant's response as a string.
    """
    body = {
        "messages": messages,
        "max_tokens": 512,
        "temperature": 0.7,
        "top_p": 1,
        "anthropic_version": "bedrock-2023-05-31"
    }
    response = bedrock.invoke_model(
        modelId=CLAUDE_MODEL_ID,
        body=json.dumps(body),
        accept="application/json",
        contentType="application/json"
    )
    result = json.loads(response["body"].read())
    # Claude 3 returns a 'content' field for the assistant's reply
    return result["content"][0]["text"]