import boto3
import os
from typing import List

def list_s3_objects(bucket_name: str, prefix: str = "") -> List[str]:
    """
    List object keys in an S3 bucket under a given prefix.
    Args:
        bucket_name (str): The name of the S3 bucket.
        prefix (str): The prefix to filter objects (optional).
    Returns:
        List[str]: List of object keys.
    """
    s3_client = boto3.client(
        "s3",
        region_name=os.getenv("AWS_REGION", "us-west-2"),
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
    )
    try:
        response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
        return [obj["Key"].rsplit("/", 1)[-1] for obj in response.get("Contents", [])]
    except Exception as e:
        print(f"Could not list S3 objects: {e}")
        return [] 