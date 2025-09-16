# test_data_preprocessing.py
import pytest
import pandas as pd
from sklearn.pipeline import Pipeline
from pre_proccess import train_churn_model
import logging
#cmd line to run this test: pytest -v results/ML/churn_prediction/data_tests.py
CSV_PATH = "C:/Users/hayde/2025-skill-build/Brazil Retail/results/csvs_in/ML_churn_features.csv"

def test_preprocessing_and_class_balance():
    results = train_churn_model(CSV_PATH, model="logistic_regression")
    pipeline = results["pipeline"]
    X_train, y_train = results["X_train"], results["y_train"]

    # Fit only the preprocessing part
    preprocessor = pipeline.named_steps["preprocessor"]
    Xt = preprocessor.fit_transform(X_train)

    # --- Check 1: No NaNs in transformed data ---
    assert not pd.DataFrame(Xt).isnull().values.any(), "NaN values found after preprocessing!"

    # --- Check 2: Target has both classes ---
    value_counts = y_train.value_counts().to_dict()
    assert all(v > 0 for v in value_counts.values()), f"Target imbalance: {value_counts}"

    # --- Check 3: Enough features created ---
    assert Xt.shape[1] > 0, "No features created after preprocessing!"
    assert Xt.shape[1] >= X_train.shape[1], "Fewer features after preprocessing than original!"

    # -- Check #4, churn column includes 1s and 0s
    logging.info(f"y_train unique values: {set(y_train.unique())}")
    logging.info(f"y_train data type: {y_train.dtype}")
    assert y_train.dtype in [int, 'int64', 'int32'], f"Unexpected target data type: {y_train.dtype}"
    assert (y_train == 0).sum() > 0, "No negative churn cases in training data!"
    assert y_train.sum() > 0, "No positive churn cases in training data!"
    assert set(y_train.unique()) == {0, 1}, f"Unexpected target values: {set(y_train.unique())}"
    assert len(y_train) == len(X_train), "Mismatch in number of samples between X and y!"


    
    