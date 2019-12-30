
import json
import os
import boto3
from pathlib import Path

def lambda_handler(event, context):
    """
    This is the doc of the lambda funtion
    """
    try:

        # Getting the client 
        s3_client = boto3.client('s3')
        
        bucket_name = event['Records'][0]['s3']['bucket']['name']
        object_name = event['Records'][0]['s3']['object']['key']

        file_name = os.path.basename(object_name)

        path = Path(f'/tmp/{file_name}')

        with path.open('wb+') as file:
            s3_client.download_fileobj(bucket_name, object_name, file)
        
        print(bucket_name, ' --- ', object_name)

    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(object_name, bucket_name))
        raise e