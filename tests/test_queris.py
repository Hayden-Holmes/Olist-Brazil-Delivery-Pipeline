from distro import name
import pytest
import pandas as pd
from pathlib import Path
from query_loader import load_queries
import expectations as EX
import query_expectations as QUERY_TESTS
from quick import generate_engine
import logging
import curated_ref as CR

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler("test.log", mode="w"),
        logging.StreamHandler()   # keep console too
    ]
)



logging.info("Logging enabled")

engine = generate_engine()

# Load all .sql files automatically
ALL_QUERIES = load_queries("queries")
logging.info("Queries %s", ALL_QUERIES)

# Base checks run on every query
QUERY_RESULTS = {}   # store query results for later checks
BASE_CHECKS = [EX.not_empty]

#Compute Reference_values
REFERENCE_VALUES= EX.compute_reference_values(engine)
logging.info("Reference values: %s", REFERENCE_VALUES)

@pytest.mark.parametrize("name, path", ALL_QUERIES.items())
def test_queries(name, path):
    logging.info("testing queries")
    logging.info("testing %s located at %s", name, path)
    if Path(path).suffix.lower() == ".sql":
        sql = Path(path).read_text()
        df = pd.read_sql_query(sql, engine)
        logging.info("Data frame created")
        QUERY_RESULTS[name]=df
        
        logging.info("Query %s\n%s", name, df.head().to_string())
        # Run base expectations
        for check in BASE_CHECKS:
            assert check(df), f"{name} failed {check.__name__}"

        # Run custom expectations
        for check in QUERY_TESTS.get(name):
            logging.info("Running custom check %s for %s", check.__name__, name)
            errors = check(df, REFERENCE_VALUES)
            if errors:
                for error in errors:
                    logging.error("Error: %s", error)
            else:
                logging.info("All checks passed for %s", name)
            assert not errors, f"{name} failed checks:\n" + "\n".join(errors)


    elif Path(path).suffix.lower()==".py":
            logging.info("skipping python files for now")
def test_single_query(ref, query_name="customers_curated"):
    path = ALL_QUERIES[query_name]
    logging.info("testing single query %s located at %s", query_name, path)
    if Path(path).suffix.lower() == ".sql":
        sql = Path(path).read_text()
        df = pd.read_sql_query(sql, engine)
        logging.info("Data frame created")
        QUERY_RESULTS[query_name]=df

        logging.info("Query %s\n%s", query_name, df.head().to_string())
        # Run base expectations
        for check in BASE_CHECKS:
            assert check(df), f"{query_name} failed {check.__name__}"

        # Run custom expectations
        for check in QUERY_TESTS.get(query_name):
            logging.info("Running custom check %s for %s", check.__name__, query_name)
            errors = check(df, ref)
            if errors:
                for error in errors:
                    logging.error("Error: %s", error)
            else:
                logging.info("All checks passed for %s", name)
            assert not errors, f"{name} failed checks:\n" + "\n".join(errors)


    elif Path(path).suffix.lower()==".py":
            logging.info("skipping python files for now")

def test_curated_queries():
    logging.info("Testing curated queries...")
    ref = CR.compute_reference_values(engine)
    logging.info("Curated reference values: %s", ref)
    for query_name in ["customers_curated", "products_curated", "orders_curated"]:
        logging.info("Testing curated query %s", query_name)
        test_single_query(ref, query_name)


def test_customers_curated():
    logging.info("Testing customers_curated query...")
    ref = CR.compute_reference_values(engine)
    logging.info("Curated reference values: %s", ref)
    test_single_query(ref, "customers_curated")

def test_products_curated():
    logging.info("Testing products_curated query...")
    ref = CR.compute_reference_values(engine)
    logging.info("Curated reference values: %s", ref)
    test_single_query(ref, "products_curated")

def test_orders_curated():
    logging.info("Testing orders_curated query...")
    ref = CR.compute_reference_values(engine)
    logging.info("Curated reference values: %s", ref)
    test_single_query(ref, "orders_curated")

