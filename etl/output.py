import csv
import os
from io import StringIO
from pathlib import Path

def decorator_to_bucket(function):
    def wrap_funct(filename):
        '''
        This funtion writes into a S3 bucket
        '''
        import boto3

        s3_client = boto3.client('s3')

        dictionary = {'bucketName': 'domfp13-s3-bucket', #This has to change for cc bucket
                'destination_blob_name': f'phoenix/{filename}',
                'source_file_name': f'/tmp/{filename}'}

        path = Path(dictionary['source_file_name'])

        with path.open("rb") as f:
            s3_client.upload_fileobj(f, dictionary['bucketName'], dictionary['destination_blob_name'])
            print("File uploaded to bucket S3")

    return wrap_funct
@decorator_to_bucket
def to_bucket(filename):
    """
    Writes a string to a gcs bucket.
    :param output: the string
    :param filename: the name of the file to write
    :return: none
    """
    from google.cloud import storage

    dictionary = {'bucketName': 'app-script-data-extraction-output',
                  'destination_blob_name': f'distribution/{filename}',
                  'source_file_name': f'/tmp/{filename}'}
    storage_client = storage.Client()
    storage_client.get_bucket(dictionary['bucketName']).blob(dictionary['destination_blob_name'])\
        .upload_from_filename(dictionary['source_file_name'])

def to_csv(filename, data, fields):
    """
    Writes a dictionary object to a csv file in gcs storage
    :param filename: the name of the file to create
    :param data: an ordered dictionary object
    :param fields: a list of fields.
    :return: none
    """
    csv.register_dialect('dblquote',
                         delimiter=',',
                         lineterminator='\n',
                         quotechar='"',
                         quoting=csv.QUOTE_ALL,
                         skipinitialspace=True)

    path = Path(f'/tmp/{filename}')
    
    # path = Path(f'{os.getcwd()}/{filename}') # This is to debugg locally

    with path.open('w', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields, dialect='dblquote')
        writer.writeheader()
        writer.writerows(data)
    
    print("CSV created")
    print("Loading to bucket")
    
    to_bucket(filename)
    
    print("Finish loading to bucket")

