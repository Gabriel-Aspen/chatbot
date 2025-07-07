import os
import boto3
import json
import time
from botocore.exceptions import ClientError

AWS_REGION = os.getenv("AWS_REGION", "us-west-2")

# Create a boto3 client for Bedrock Agent Runtime

# You must provide your own knowledge base ID and model ARN
# inference_profile_id = "us.anthropic.claude-3-7-sonnet-20250219-v1:0"


def retrieve_and_generate_with_kb(messages, knowledge_base_id, inference_profile_id, user_id="user-1", max_retries=10):
    """
    Uses Bedrock Agent Runtime's retrieve_and_generate to answer a question using a knowledge base.
    messages: list of dicts with 'role' and 'content' keys (like OpenAI format)
    user_id: unique identifier for the user/session
    max_retries: maximum number of retry attempts for auto-pause errors
    Returns the assistant's response as a string.
    """

    agent_client = boto3.client(
        "bedrock-agent-runtime",
        region_name=AWS_REGION,
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    )

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
                        "knowledgeBaseId": knowledge_base_id,
                        "modelArn": inference_profile_id
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

def sync_knowledge_base(knowledge_base_id, dataSourceId, max_retries=3):
    """
    Syncs a knowledge base to ensure it's up to date with the latest data sources.
    
    Args:
        knowledge_base_id (str): The ID of the knowledge base to sync
        max_retries (int): Maximum number of retry attempts
    
    Returns:
        dict: The sync response or None if failed
    """
    agent_client = boto3.client(
        "bedrock-agent",
        region_name=AWS_REGION,
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    )

    for attempt in range(max_retries + 1):
        try:
            response = agent_client.start_ingestion_job(
                knowledgeBaseId=knowledge_base_id,
                dataSourceId=dataSourceId
            )
            
            print(f"Knowledge base sync started. Job ID: {response.get('ingestionJob', {}).get('ingestionJobId')}")
            return response
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            
            if error_code == 'ValidationException' and ("auto-paused" in error_message.lower() or "resuming" in error_message.lower()):
                if attempt < max_retries:
                    wait_time = (2 ** attempt) + 1
                    print(f"Database is resuming from auto-pause. Waiting {wait_time} seconds before retry {attempt + 1}/{max_retries}...")
                    time.sleep(wait_time)
                    continue
                else:
                    print("Knowledge base sync failed after max retries due to database maintenance.")
                    return None
            else:
                print(f"Error syncing knowledge base: {error_message}")
                return None
        except Exception as e:
            print(f"An error occurred while syncing the knowledge base: {str(e)}")
            return None

def get_knowledge_base_status(knowledge_base_id):
    """
    Gets the current status of a knowledge base.
    
    Args:
        knowledge_base_id (str): The ID of the knowledge base
    
    Returns:
        dict: The knowledge base status or None if failed
    """
    try:
        response = agent_client.get_knowledge_base(
            knowledgeBaseId=knowledge_base_id
        )
        return response.get('knowledgeBase', {})
    except Exception as e:
        print(f"Error getting knowledge base status: {str(e)}")
        return None

def list_knowledge_bases():
    """List all Bedrock knowledge bases in the account."""
    client = boto3.client('bedrock-agent')
    paginator = client.get_paginator('list_knowledge_bases')
    knowledge_bases = []
    for page in paginator.paginate():
        knowledge_bases.extend(page.get('knowledgeBaseSummaries', []))
    return knowledge_bases


def get_knowledge_base_by_name(name):
    """Fetch a Bedrock knowledge base by its name, including data source info."""
    client = boto3.client('bedrock-agent')
    # List all knowledge bases and match by name
    for kb in list_knowledge_bases():
        if kb.get('name') == name:
            kb_id = kb.get('knowledgeBaseId')
            kb_info = {}
            kb_info['kb_id'] = kb_id
            # kb_info = client.get_knowledge_base(knowledgeBaseId=kb_id).get('knowledgeBase')
            # List data sources for this knowledge base
            # kb_info['dataSources'] = data_sources
            data_sources = client.list_data_sources(knowledgeBaseId=kb_id).get('dataSourceSummaries', [])
            kb_info['data_sources'] = data_sources
            return kb_info
    return None 