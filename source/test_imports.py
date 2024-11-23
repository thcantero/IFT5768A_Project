# test_imports.py
try:
    from catboost import CatBoostClassifier
    print("CatBoost imported successfully.")
except Exception as e:
    print(f"Error importing CatBoost: {e}")

try:
    import xgboost
    print("XGBoost imported successfully.")
except Exception as e:
    print(f"Error importing XGBoost: {e}")

try:
    import tensorflow as tf
    print("TensorFlow imported successfully.")
except Exception as e:
    print(f"Error importing TensorFlow: {e}")
