

def generate_engine():
    print("Generating DB engine...")
    import os
    from sqlalchemy import create_engine
    import json

    config_txt = os.path.join(os.path.dirname(__file__), "creds", "db_config.json")
    print(f"Loading DB config from {config_txt}")
    with open(config_txt) as f:
        config = json.load(f)

    DB_HOST = config["DB_HOST"]
    DB_PORT = config["DB_PORT"]
    DB_NAME = config["DB_NAME"]
    DB_USER = config["DB_USER"]
    DB_PASS = config["DB_PASS"]

    print(f"Connecting to DB {DB_NAME} at {DB_HOST}:{DB_PORT} as user {DB_USER}")
    engine = create_engine(
        f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    print("Connection Sucessful")
    return engine


