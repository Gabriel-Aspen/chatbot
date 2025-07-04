import os
import boto3
import json
import time
from botocore.exceptions import ClientError

AWS_REGION = os.getenv("AWS_REGION", "us-west-2")

# Create a boto3 client for Bedrock Agent Runtime
agent_client = boto3.client(
    "bedrock-agent-runtime",
    region_name=AWS_REGION,
)

# You must provide your own knowledge base ID and model ARN
KNOWLEDGE_BASE_ID = os.getenv("BEDROCK_KNOWLEDGE_BASE_ID", "6YC60AQVKG")
MODEL_ARN = os.getenv("BEDROCK_MODEL_ARN", "us.anthropic.claude-3-7-sonnet-20250219-v1:0")


def retrieve_and_generate_with_kb(messages, user_id="user-1", max_retries=3):
    """
    Uses Bedrock Agent Runtime's retrieve_and_generate to answer a question using a knowledge base.
    messages: list of dicts with 'role' and 'content' keys (like OpenAI format)
    user_id: unique identifier for the user/session
    max_retries: maximum number of retry attempts for auto-pause errors
    Returns the assistant's response as a string.
    """
    # The last user message is the query
    user_message = next((m["content"] for m in reversed(messages) if m["role"] == "user"), "")
    if not user_message:
        return "No user message found."

    for attempt in range(max_retries + 1):
        try:
            response = agent_client.retrieve_and_generate(
                input={"text": user_message},
                retrieveAndGenerateConfiguration={
                    "knowledgeBaseConfiguration": {
                        "knowledgeBaseId": KNOWLEDGE_BASE_ID,
                        "modelArn": MODEL_ARN
                    },
                    "type": "KNOWLEDGE_BASE"
                }
            )
            # The response format may vary; check AWS docs for details
            return response["output"]["text"]
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            
            if error_code == 'ValidationException' and ("auto-paused" in error_message.lower() or "resuming" in error_message.lower()):
                if attempt < max_retries:
                    wait_time = (2 ** attempt) + 1  # Exponential backoff: 2s, 3s, 5s
                    print(f"Database is resuming from auto-pause. Waiting {wait_time} seconds before retry {attempt + 1}/{max_retries}...")
                    time.sleep(wait_time)
                    continue
                else:
                    return "Sorry, the knowledge base is currently unavailable due to database maintenance. Please try again in a few moments."
            else:
                # Re-raise if it's not an auto-pause error
                raise e
        except Exception as e:
            return f"An error occurred while processing your request: {str(e)}" 