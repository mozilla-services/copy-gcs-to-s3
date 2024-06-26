import os
import re
import tempfile
import logging
import boto3
from google.cloud import storage

# Initialize logging
logging.basicConfig(level=logging.INFO)

# Initialize the Google Cloud Storage client
gcs_client = storage.Client()

# Initialize the S3 client with the retrieved credentials
s3_client = boto3.client('s3',
                         aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                         aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"))

S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

SKIP_PATH_REGEXES = [
    "^pub/firefox/nightly/partials",
    "^pub/thunderbird/nightly/partials",
    "^to-be-deleted",
]

def should_skip(file_name):
    """Check if the file_name matches any of the skip path regexes."""
    for regex in SKIP_PATH_REGEXES:
        if re.match(regex, file_name):
            return True
    return False

def copy_to_s3(event, context):
    """Triggered by a change to a Cloud Storage bucket.
    Args:
        event (dict): Event payload.
        context (google.cloud.functions.Context): Metadata for the event.
    """
    logging.info("Received event: %s", event)
    
    # Get the file details from the event
    bucket_name = event['bucket']
    file_name = event['name']
    logging.info(f"Processing file: {file_name} from bucket: {bucket_name}")

    if should_skip(file_name):
        logging.info(f"SKIP_PATH_REGEXES matches file '{file_name}'. Skipping")
        return

    # Download the file from GCS to a temporary location
    try:
        bucket = gcs_client.bucket(bucket_name)
        blob = bucket.blob(file_name)
        
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_file.close()
        
        blob.download_to_filename(temp_file.name)
        logging.info(f"Downloaded file: {file_name} to temporary location")
    except Exception as e:
        logging.error(f"Error downloading file from GCS: {e}")
        return

    # Upload the file to S3 with Glacier Deep Archive storage class
    try:
        s3_client.upload_file(
            temp_file.name,
            S3_BUCKET_NAME,
            file_name,
            ExtraArgs={'StorageClass': 'DEEP_ARCHIVE'}
        )
        logging.info(f"Uploaded file: {file_name} to S3 bucket: {S3_BUCKET_NAME} with Glacier Deep Archive storage class")
    except Exception as e:
        logging.error(f"Error uploading file to S3: {e}")
    finally:
        # Clean up the temporary file
        os.remove(temp_file.name)
        logging.info(f"Removed temporary file: {temp_file.name}")

