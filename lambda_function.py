import json
import os
from pathlib import Path

# Local libs
from etl.extract import (
    parse_CADTechData, parse_CADTechDataOG, parse_Ingram_Micro_BMO, parse_synnex,
    parse_ingram, parse_techdata, parse_ingramCAD
)

"""
Register processes here:
"""
REGISTRY = {
    # filename : function
    'DBI_LOAD_0001.xls':  parse_CADTechData,
    'DBI_LOAD_0002.xls':  parse_CADTechDataOG,
    'DBI_LOAD_0003.xlsx': parse_Ingram_Micro_BMO,
    'DBI_LOAD_0004.xls':  parse_synnex,
    'DBI_LOAD_0005.xlsx': parse_ingram,
    'DBI_LOAD_0007.xlsx': parse_techdata,
    'DBI_LOAD_0008.xls':  parse_ingramCAD
}

def lambda_handler(event, context):
    """
    Triggered by a change to a AWS Bucket 
    Args:
        event (dict): Event payload.
        contex: Metadata for the event
    Return:
        None
    """
    try:

        def decorator_process(function):
            def wrap_funct(event, context):
                """
                This is for AWS
                """
                print("-----Begin-----")
                import boto3
                s3_client = boto3.client('s3')
        
                bucket_name = event['Records'][0]['s3']['bucket']['name']
                object_name = event['Records'][0]['s3']['object']['key']

                file_name = os.path.basename(object_name)

                path = Path(f'/tmp/{file_name}')

                with path.open('wb+') as file:
                    s3_client.download_fileobj(bucket_name, object_name, file)
                
                REGISTRY[file_name](file.name)

                print("-----End-----")
            return wrap_funct
        @decorator_process
        def process_event(event, context):
            """
            This is for GCP
            """
            from google.cloud import storage

            file_name = os.path.basename(event['name'])
        
            if file_name in REGISTRY.keys():
                client = storage.Client()
                path = Path(f'/tmp/{file_name}')

                with path.open('wb+') as file:
                    client.bucket(event['bucket']).get_blob(event['name']).download_to_file(file)

                REGISTRY[file_name](file.name)

        process_event(event, context)

    except Exception as e:
        print(e)
        raise e