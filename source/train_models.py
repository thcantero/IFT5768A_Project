import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, roc_curve, accuracy_score
from sklearn.ensemble import RandomForestClassifier, VotingClassifier, StackingClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.calibration import calibration_curve
import xgboost as xgb
import lightgbm as lgb
from catboost import CatBoostClassifier

import wandb

# Load preprocessed data
data = pd.read_csv("data/preprocessed_data.csv")
X = data.drop(columns=['isGoal'])
y = data['isGoal']

# Split data
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

# Initialize WandB
wandb.init(project="xG-best-model", job_type="training")

# Define Models
models = {
    "Logistic Regression": LogisticRegression(),
    "Decision Tree": DecisionTreeClassifier(max_depth=10, random_state=42),
    "Random Forest": RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42),
    "XGBoost": xgb.XGBClassifier(learning_rate=0.1, max_depth=6, n_estimators=150, use_label_encoder=False),
    "LightGBM": lgb.LGBMClassifier(learning_rate=0.1, max_depth=6, n_estimators=150),
    "CatBoost": CatBoostClassifier(iterations=150, learning_rate=0.1, depth=6, verbose=False),
    "KNN": KNeighborsClassifier(n_neighbors=5),
    "SVM": SVC(probability=True, kernel='linear', random_state=42)
}

# Train and Evaluate Models
results = {}
for name, model in models.items():
    model.fit(X_train, y_train)
    y_pred = model.predict_proba(X_val)[:, 1] if hasattr(model, "predict_proba") else model.decision_function(X_val)
    auc = roc_auc_score(y_val, y_pred)
    results[name] = {"model": model, "auc": auc}

    # Log AUC to WandB
    wandb.log({f"{name} AUC": auc})

    # ROC Curve
    fpr, tpr, _ = roc_curve(y_val, y_pred)
    wandb.log({f"{name} ROC Curve": wandb.plot.line_series(
        xs=fpr, ys=[tpr], keys=["True Positive Rate"], title=f"{name} ROC Curve",
        xname="False Positive Rate"
    )})

    # Calibration Curve
    prob_true, prob_pred = calibration_curve(y_val, y_pred, n_bins=10)
    wandb.log({f"{name} Calibration Curve": wandb.plot.line_series(
        xs=prob_pred, ys=[prob_true], keys=["True Probability"], title=f"{name} Calibration Curve",
        xname="Predicted Probability"
    )})


# Ensemble Models
voting_clf = VotingClassifier(estimators=[
    ("lr", models["Logistic Regression"]),
    ("rf", models["Random Forest"]),
    ("xgb", models["XGBoost"]),
], voting='soft')
voting_clf.fit(X_train, y_train)
y_pred_voting = voting_clf.predict_proba(X_val)[:, 1]
auc_voting = roc_auc_score(y_val, y_pred_voting)
wandb.log({"Voting Classifier AUC": auc_voting})

# Save the best model
best_model_name = max(results, key=lambda k: results[k]["auc"])
best_model = results[best_model_name]["model"]
wandb.save(f"{best_model_name}.model")
