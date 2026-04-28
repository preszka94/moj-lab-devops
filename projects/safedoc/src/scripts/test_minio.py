import boto3
from botocore.exceptions import NoCredentialsError, ClientError
import sys

# Connection configuration to our local MinIO
s3 = boto3.client('s3',
    endpoint_url='http://localhost:9000', # Note: port 9000 (API), not 9001 (Console)
    aws_access_key_id='admin',     # ENTER YOUR LOGIN HERE (from docker-compose)
    aws_secret_access_key='password123'  # ENTER YOUR PASSWORD HERE (from docker-compose)
)

bucket_name = 'devops-test-bucket'
file_name = 'test_file.txt'
content = 'Hello MinIO! This is a test from Python.'

def create_bucket_and_upload():
    # STEP 1: Safely create a bucket
    try:
        s3.create_bucket(Bucket=bucket_name)
        print(f"✅ Bucket '{bucket_name}' created successfully.")
    except ClientError as e:
        # If the bucket exists, an error will appear, but we catch it and move on 🔄
        print(f"ℹ️ Info: Bucket already exists or another error occurred. Moving on!")

    # Prepare local test file
    with open(file_name, 'w') as f:
        f.write(content)

    # STEP 2: Safely upload file (this will always execute, regardless of Step 1)
    try:
        s3.upload_file(file_name, bucket_name, 'invoice_001.txt')
        print(f"✅ File '{file_name}' uploaded to MinIO as 'invoice_001.txt'.")
        sys.exit(0) # Returns code 0 (success) for future Bash/ADO pipelines [cite: 280]
    except ClientError as e:
        print(f"❌ Error uploading file: {e}")
        sys.exit(1) # Returns code 1 (error), which would stop the pipeline [cite: 280, 294]

if __name__ == '__main__':
    
    create_bucket_and_upload()