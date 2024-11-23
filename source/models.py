import wandb
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import roc_auc_score, accuracy_score, f1_score, log_loss, confusion_matrix
from evaluate_model import evaluate_model
from create_graphs import create_wandb_graphs
import lightgbm as lgb
from lightgbm import LGBMClassifier
from xgboost import XGBClassifier
from catboost import CatBoostClassifier
from sklearn.neighbors import KNeighborsClassifier
import joblib

#Random Forest Model
def random_forest(project, job_type, name, n_estimators, max_depth, X_train, y_train, X_val, y_val):
    # Ensure y_train and y_val are 1D arrays
    y_train = y_train.values.ravel() if isinstance(y_train, pd.DataFrame) else y_train
    y_val = y_val.values.ravel() if isinstance(y_val, pd.DataFrame) else y_val
    
    # Initiate WandB
    wandb.init(project=project, job_type=job_type, name=name)
    
    # Train model
    model = RandomForestClassifier(n_estimators=n_estimators, max_depth=max_depth, random_state=42)
    model.fit(X_train, y_train)

    # Evaluate model
    y_preds_proba = model.predict_proba(X_val)[:, 1]
    y_pred = (y_preds_proba > 0.5).astype(int)
    evaluate_model(y_val, y_preds_proba, y_pred)
    
    create_wandb_graphs(y_val, y_preds_proba, name)

    # Feature Importance
    if isinstance(X_train, pd.DataFrame):
        feature_importance = pd.DataFrame({
            "Feature": X_train.columns,
            "Importance": model.feature_importances_
        }).sort_values(by="Importance", ascending=False)
        print("Feature Importance:")
        print(feature_importance)
        wandb.log({"Feature Importance": wandb.Table(dataframe=feature_importance)})
    else:
        print("Feature importance logging skipped. X_train is not a DataFrame.")

#Decision Tree
def decision_tree(project, job_type, name, max_depth, X_train, y_train, X_val, y_val):
    
    #Initiate wandb
    wandb.init(project=project, job_type=job_type, name=name)

    #Train model
    model = DecisionTreeClassifier(max_depth=max_depth, random_state=42)
    model.fit(X_train, y_train)

    # Evaluate model
    y_preds_proba = model.predict_proba(X_val)[:, 1]
    y_pred = (y_preds_proba > 0.5).astype(int)
    evaluate_model(y_val, y_preds_proba, y_pred)
    
    create_wandb_graphs(y_val, y_preds_proba, name)

    # Feature Importance
    if isinstance(X_train, pd.DataFrame):
        feature_importance = pd.DataFrame({
            "Feature": X_train.columns,
            "Importance": model.feature_importances_
        }).sort_values(by="Importance", ascending=False)
        print("Feature Importance:")
        print(feature_importance)
        wandb.log({"Feature Importance": wandb.Table(dataframe=feature_importance)})
    else:
        print("Feature importance logging skipped. X_train is not a DataFrame.")


#LigthGBM
def lightgbm(project, job_type, name, learning_rate, max_depth, n_estimators, X_train, y_train, X_val, y_val):
    
    #Initiate wandb
    wandb.init(project=project, job_type=job_type, name=name)

    # Train LightGBM
    model = lgb.LGBMClassifier(learning_rate=learning_rate, max_depth=max_depth, n_estimators=n_estimators, random_state=42)
    model.fit(X_train, y_train)

    joblib.dump(model, "lightgbm_model.pkl")
    
    # Evaluate
    y_pred = model.predict_proba(X_val)[:, 1]
    auc = roc_auc_score(y_val, y_pred)

    # Evaluate model
    y_preds_proba = model.predict_proba(X_val)[:, 1]
    y_pred = (y_preds_proba > 0.5).astype(int)
    evaluate_model(y_val, y_preds_proba, y_pred)
    
    create_wandb_graphs(y_val, y_preds_proba, name)

    # Feature Importance
    if isinstance(X_train, pd.DataFrame):
        feature_importance = pd.DataFrame({
            "Feature": X_train.columns,
            "Importance": model.feature_importances_
        }).sort_values(by="Importance", ascending=False)
        print("Feature Importance:")
        print(feature_importance)
        wandb.log({"Feature Importance": wandb.Table(dataframe=feature_importance)})
    else:
        print("Feature importance logging skipped. X_train is not a DataFrame.")


#XGBoost 
def xg_boost(project, job_type, name, n_estimators, learning_rate, max_depth, X_train, y_train, X_val, y_val):
    
    #Initiate wandb
    wandb.init(project=project, job_type=job_type, name=name)

    #Train model
    model = XGBClassifier(n_estimators=n_estimators, max_depth=max_depth, learning_rate = learning_rate, use_label_encoder=False, eval_metric="logloss", random_state=42)
    model.fit(X_train, y_train)

     # Evaluate model
    y_preds_proba = model.predict_proba(X_val)[:, 1]
    y_pred = (y_preds_proba > 0.5).astype(int)
    evaluate_model(y_val, y_preds_proba, y_pred)
    
    create_wandb_graphs(y_val, y_preds_proba, name)

    # Feature Importance
    if isinstance(X_train, pd.DataFrame):
        feature_importance = pd.DataFrame({
            "Feature": X_train.columns,
            "Importance": model.feature_importances_
        }).sort_values(by="Importance", ascending=False)
        print("Feature Importance:")
        print(feature_importance)
        wandb.log({"Feature Importance": wandb.Table(dataframe=feature_importance)})
    else:
        print("Feature importance logging skipped. X_train is not a DataFrame.")


# CatBoost
def cat_boost(project, job_type, name, iterations, learning_rate, depth, X_train, y_train, X_val, y_val):

    #Initiate wandb
    wandb.init(project=project, job_type=job_type, name=name)

    # Train CatBoost
    model = CatBoostClassifier(iterations=iterations, learning_rate=learning_rate, depth=depth, verbose=False, random_state=42)
    model.fit(X_train, y_train)

    # Evaluate model
    y_preds_proba = model.predict_proba(X_val)[:, 1]
    y_pred = (y_preds_proba > 0.5).astype(int)
    evaluate_model(y_val, y_preds_proba, y_pred)
    
    create_wandb_graphs(y_val, y_preds_proba, name)

    # Feature Importance
    if isinstance(X_train, pd.DataFrame):
        feature_importance = pd.DataFrame({
            "Feature": X_train.columns,
            "Importance": model.feature_importances_
        }).sort_values(by="Importance", ascending=False)
        print("Feature Importance:")
        print(feature_importance)
        wandb.log({"Feature Importance": wandb.Table(dataframe=feature_importance)})
    else:
        print("Feature importance logging skipped. X_train is not a DataFrame.")

# KNN
def knn(project, job_type, name, n_neighbors, X_train, y_train, X_val, y_val):

    #Initiate wandb
    wandb.init(project=project, job_type=job_type, name=name)


    # Train KNN
    model = KNeighborsClassifier(n_neighbors=n_neighbors)
    model.fit(X_train, y_train)

    # Evaluate model
    y_preds_proba = model.predict_proba(X_val)[:, 1]
    y_pred = (y_preds_proba > 0.5).astype(int)
    evaluate_model(y_val, y_preds_proba, y_pred)
    
    create_wandb_graphs(y_val, y_preds_proba, name)


