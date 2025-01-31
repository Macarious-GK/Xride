import boto3
from botocore.exceptions import NoCredentialsError, ClientError
from django.conf import settings

def Manage_S3_Media(file_path, action):
    # Initialize the S3 client
    s3_client = boto3.client(
        's3',
        aws_access_key_id= settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key= settings.AWS_SECRET_ACCESS_KEY
    )
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    print(f'Performing {action} operation on {file_path} in {bucket_name}...')
    if action == 'delete':
        try:
            # Delete the specified file
            s3_client.delete_object(Bucket=bucket_name, Key=file_path)
            print(f'Successfully deleted {file_path} from {bucket_name}.')
        except NoCredentialsError:
            print('Credentials not available.')
        except ClientError as e:
            print(f'Error occurred: {e}')
    if action == 'upload':
        try:
            # Upload the specified file
            s3_client.upload_file(file_path, bucket_name, file_path)
            print(f'Successfully uploaded {file_path} to {bucket_name}.')
        except NoCredentialsError:
            print('Credentials not available.')
        except ClientError as e:
            print(f'Error occurred: {e}')