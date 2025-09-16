
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
import json
import traceback
with open("creds/db_config.json") as f:
    config = json.load(f)

    DB_HOST = config["DB_HOST"]
    DB_PORT = config["DB_PORT"]
    DB_NAME = config["DB_NAME"]
    DB_USER = config["DB_USER"]
    DB_PASS = config["DB_PASS"]
def main():
   



    engine = create_engine(
        f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}", echo=True
    )

    # --- 2. CSV file paths ---

    BASE_DIR = os.path.dirname(__file__)
    DATA_DIR = os.path.join(BASE_DIR, "..", "db_csvs")

    DATA_FILES = {
        # "customers": os.path.join(DATA_DIR, "olist_customers_dataset.csv"),
        # "sellers": os.path.join(DATA_DIR, "olist_sellers_dataset.csv"),
        # "orders": os.path.join(DATA_DIR, "olist_orders_dataset.csv"),
        # "order_items": os.path.join(DATA_DIR, "olist_order_items_dataset.csv"),
        # "products": os.path.join(DATA_DIR, "olist_products_dataset.csv"),

        "geolocation": os.path.join(DATA_DIR, "olist_geolocation_dataset.csv"),
        # "order_payments": os.path.join(DATA_DIR, "olist_order_payments_dataset.csv"),
        # "order_reviews": os.path.join(DATA_DIR, "olist_order_reviews_dataset.csv"),
        # "product_category_name_translation": os.path.join(DATA_DIR, "product_category_name_translation.csv")
    }

    # --- 3. Load each dataset ---
    for table_name, file_path in DATA_FILES.items():
        print(f"Loading {table_name} from {file_path} ...")
        
        # Load CSV into DataFrame
        df = pd.read_csv(file_path)
        if table_name == "order_reviews":
            # Drop duplicates in order_reviews based on review_id
            df = df.drop_duplicates(subset=["review_id"])
        
        # Upload to Postgres
        print(f"Uploading {len(df)} rows to {table_name} ...")
        try:
            df.to_sql(
                table_name,
                engine,
                if_exists="replace",   # 🔑 Drop + recreate table
                index=False,
                method="multi",        # batch insert
                chunksize=10_000       # send 10k rows per statement
            )
            print(f"Uploaded {len(df)} rows to {table_name}")
        except Exception as e:
            print(f"Error loading {table_name}: {e}")
            traceback.print_exc()
        print("-" * 40)


def load_geo_location():
    # Load geolocation data
    print("Loading geolocation data ...")
    engine = create_engine(
        f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}", echo=True
    )
# customers.csv should contain the key column you match on
    cust = pd.read_csv("db_csvs/olist_customers_dataset.csv")
    cust_zips = set(cust["customer_zip_code_prefix"].unique())

    geo_iter = pd.read_csv("db_csvs/olist_geolocation_dataset.csv", chunksize=100_000)

    filtered_chunks = []
    for chunk in geo_iter:
        mask = chunk["geolocation_zip_code_prefix"].isin(cust_zips)
        filtered_chunks.append(chunk[mask])

    geo_filtered = pd.concat(filtered_chunks, ignore_index=True)
    print(len(geo_filtered))   # should be close to 99k (plus duplicates)

    # Insert only the filtered rows
    geo_filtered.to_sql(
        "geolocation_filtered",
        engine,
        if_exists="replace",
        index=False,
        method="multi",
        chunksize=10_000
    )

if __name__ == "__main__":
    # main()
    load_geo_location()
    # raise RuntimeError("This script is not intended to be run directly.")