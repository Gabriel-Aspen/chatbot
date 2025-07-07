import boto3
import json
import os

def invoke_lambda_function(parameters):
    """
    Invokes a Lambda function with the specified payload structure.
    
    Args:
        action_group (str): The action group value
        function_name (str): The function value
        message_version (str): The message version value
        parameters (list): List of parameter dictionaries with name, type, and value
    
    Returns:
        dict: The Lambda response
    """

    function_name = "aspentech-pdf-processor"

    # Create a Lambda client
    lambda_client = boto3.client(
        'lambda',
        region_name=os.getenv("AWS_REGION", "us-west-2"),
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
    )
        
    try:
        # Invoke the Lambda function
        response = lambda_client.invoke(
            FunctionName=function_name,
            InvocationType='RequestResponse',  # Synchronous invocation
            Payload=json.dumps(parameters)
        )
        
        # Parse the response
        response_payload = json.loads(response['Payload'].read())
        return response_payload
        
    except Exception as e:
        # print(f"Error invoking Lambda function: {str(e)}")
        print(f"Error invoking Lambda function")
        return None