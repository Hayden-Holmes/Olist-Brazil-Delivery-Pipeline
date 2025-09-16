import os
import logging
import pandas as pd
import boto3
from pathlib import Path
from sqlalchemy import text
import sys
from pathlib import Path

# Add root directory to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from quick import generate_engine
from s3_methods import connect_s3

# --- CONFIG ---
LOCAL_OUTPUT_DIR = Path("results/csvs_out")
LOCAL_INPUT_DIR = Path("results/csvs_in")
BUCKET_NAME = "brazil-retail-results"
BASE_DIR = Path(__file__).resolve().parent   # directory of main.py (results/)


# --- LOGGING SETUP ---
LOG_FILE = "etl.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# 1. Extract → run queries and save results as CSV
def extract_and_save_query(name, path, engine):
    LOCAL_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

   


    logger.info("Starting extract_and_save_queries")

    try:
        sql = Path(path).read_text()
        df = pd.read_sql_query(text(sql), engine)
        csv_path = LOCAL_OUTPUT_DIR / f"{name}.csv"
        df.to_csv(csv_path, index=False)
        logger.info("Saved %s (%d rows) → %s", name, len(df), csv_path)
    except Exception as e:
            logger.error("Failed to run query %s at %s: %s", name, path, e)
    return {name: csv_path}


# 2. Load → upload CSVs to S3
def upload_file_to_s3(local_file, s3):
    logger.info("Uploading %s to S3 bucket %s", local_file, BUCKET_NAME)

    key = f"results/output_csvs/{Path(local_file).name}"
    try:
        s3.upload_file(str(local_file), BUCKET_NAME, key)
        logger.info("Uploaded %s → s3://%s/%s", local_file, BUCKET_NAME, key)
    except Exception as e:
        logger.error("Error uploading %s: %s", local_file, e)


# 3. Download → sync CSVs from S3 to local results/csvs_in
def download_file_from_s3(key, s3):
    LOCAL_INPUT_DIR.mkdir(parents=True, exist_ok=True)
    try:
            filename = Path(key).name
            local_path = LOCAL_INPUT_DIR / filename

            s3.download_file(BUCKET_NAME, key, str(local_path))
            logger.info("⬇Downloaded %s → %s", key, local_path)
    except Exception as e:
        logger.error("Failed to download from S3: %s", e)

#read/write all quries
def extract_and_save_queries():
  query_files = list(Path("queries").rglob("*.sql"))
  results = {}
  engine= generate_engine()
  for path in query_files:
      name = f"{path.parent.name}_{path.stem}"
      result = extract_and_save_query(name, path, engine)
      results.update(result)
  return results
def exd_key(key: str, path: str):
    """
    Run a single SQL query (from path), save as CSV with 'key' as the filename,
    upload to S3, and download it back locally.
    """
    engine = generate_engine()   # DB engine for SQLAlchemy
    s3 = connect_s3()            # boto3 S3 client

    name = Path(key).stem  # remove .csv extension if passed
    try:
        # 1. Run SQL & save locally
        result = extract_and_save_query(name, path, engine)

        # 2. Upload the CSV to S3
        local_csv = LOCAL_OUTPUT_DIR / f"{name}.csv"
        upload_file_to_s3(local_csv, s3)

        # 3. Download it back from S3
        s3_key = f"results/output_csvs/{local_csv.name}"
        download_file_from_s3(s3_key, s3)

        return result
    except Exception as e:
        logger.error("exd_key failed for %s: %s", key, e)
        return {}
    


def upload_to_s3():
    s3=connect_s3()
    for file in LOCAL_OUTPUT_DIR.glob("*.csv"):
        upload_file_to_s3(file, s3)

def download_from_s3():
    s3=connect_s3()
    files=s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix="results/output_csvs/")
    for file in files.get('Contents', []):
        download_file_from_s3(file['Key'], s3)

#only for new queries
def is_new_file(file,s3):
    logger.info("Checking if %s is new in S3", file.name)
    s3 = connect_s3()
    s3_key = f"results/output_csvs/{file.name}"
   
    try:
        s3.head_object(Bucket=BUCKET_NAME, Key=s3_key)
        return False  # File exists in S3
    except s3.exceptions.ClientError as e:
        if e.response['Error']['Code'] == '404':
            return True  # File does not exist in S3
        else:
            logger.error("Error checking file in S3: %s", e)
            return False

def extract_and_save_new_queries():
    s3 = connect_s3()
    query_files = list(Path("queries").rglob("*.sql"))
    results = {}
    engine = generate_engine()
    for path in query_files:
        name = f"{path.parent.name}_{path.stem}"
        if is_new_file(LOCAL_OUTPUT_DIR / f"{name}.csv", s3):
            logger.info("Extracting and saving NEW query %s", name)
            result = extract_and_save_query(name, path, engine)
            results.update(result)
    return results

def upload_new_to_s3():
    s3 = connect_s3()
    for file in LOCAL_OUTPUT_DIR.glob("*.csv"):
        if is_new_file(file,s3):
            logger.info("Uploading NEW %s to S3", file.name)
            upload_file_to_s3(file, s3)

def download_new_from_s3():
    s3=connect_s3()
    files=s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix="results/output_csvs/")
    for file in files.get('Contents', []):
        local_path = LOCAL_INPUT_DIR / Path(file['Key']).name
        if not local_path.exists():
            logger.info("Downloading NEW %s from S3", file['Key'])
            download_file_from_s3(file['Key'], s3)
def exd_new():
    extract_and_save_new_queries()
    upload_new_to_s3()
    download_new_from_s3()

# 4. Create DataFrame loader
def load_csv_as_df(name: str) -> pd.DataFrame:
    """Load a specific CSV (by filename without extension) into a pandas DataFrame"""
    logging.info("Loading %s.csv into DataFrame", name)
    file_path = name
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        logger.error("File not found: %s", file_path)
        return pd.DataFrame()  # Return an empty DataFrame on error
    logger.info("Loaded %s.csv (%d rows)", name, len(df))
    return df




# --- MAIN ---
# if __name__ == "__main__":
#     # results = extract_and_save_queries()
#     # upload_to_s3()
#     download_from_s3()
