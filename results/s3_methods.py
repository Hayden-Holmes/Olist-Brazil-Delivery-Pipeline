import boto3
import boto3
from botocore.exceptions import NoCredentialsError
import logging
import os

logging.basicConfig(level=logging.INFO)

# --- Setup S3 client ---
def connect_s3():
    """
    Creates an S3 client using credentials from aws configure or env vars.
    """
    try:
        s3 = boto3.client("s3")
    except Exception as e:
        logging.error("Error connecting to S3: %s", e)
    return s3

def upload_file(local_path: str, bucket_name: str, s3_key: str):
    """
    Upload a file from local_path to s3://bucket_name/s3_key
    """
    s3 = connect_s3()
    try:
        s3.upload_file(local_path, bucket_name, s3_key)
        logging.info(f" Uploaded {local_path} to s3://{bucket_name}/{s3_key}")
    except FileNotFoundError:
        logging.error(" The file was not found: %s", local_path)
    except NoCredentialsError:
        logging.error(" AWS credentials not available.")


def upload_all_csvs(bucket_name: str, folder="results/out_put_csvs"):
    """
    Upload all CSV files from the local folder to the S3 bucket.
    Keeps the same file names.
    """
    s3 = connect_s3()
    for file in os.listdir(folder):
        if file.endswith(".csv"):
            local_path = os.path.join(folder, file)
            s3_key = f"out_put_csvs/{file}"  # folder path inside S3
            upload_file(local_path, bucket_name, s3_key)

def get_file(bucket_name: str, s3_key: str, local_path: str):
    """
    Download a file from s3://bucket_name/s3_key to local_path
    """
    s3 = connect_s3()
    try:
        s3.download_file(bucket_name, s3_key, local_path)
        logging.info(f"Downloaded s3://{bucket_name}/{s3_key} to {local_path}")
    except FileNotFoundError:
        logging.error(" The file was not found: %s", local_path)
    except NoCredentialsError:
        logging.error(" AWS credentials not available.")

def get_all_csvs(bucket_name: str, folder="results/out_put_csvs"):
    """
    Download all CSV files from the S3 bucket folder to the local folder.
    Keeps the same file names.
    """
    s3 = connect_s3()
    try:
        response = s3.list_objects_v2(Bucket=bucket_name, Prefix="out_put_csvs/")
        if 'Contents' in response:
            for obj in response['Contents']:
                s3_key = obj['Key']
                if s3_key.endswith(".csv"):
                    file_name = os.path.basename(s3_key)
                    local_path = os.path.join(folder, file_name)
                    get_file(bucket_name, s3_key, local_path)
        else:
            logging.info("No files found in the specified S3 folder.")
    except NoCredentialsError:
        logging.error(" AWS credentials not available.")