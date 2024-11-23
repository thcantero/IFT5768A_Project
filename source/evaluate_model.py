import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score, log_loss, accuracy_score, f1_score, confusion_matrix
import wandb

def evaluate_model(y_val, y_preds_proba, y_preds):
    
    # Calculate metrics
    auc_score = roc_auc_score(y_val, y_preds_proba)
    log_loss_score = log_loss(y_val, y_preds_proba)
    accuracy = accuracy_score(y_val, y_preds)
    f1 = f1_score(y_val, y_preds)

    # Log metrics to WandB
    wandb.log({"AUC": auc_score, "Log Loss": log_loss_score, "Accuracy": accuracy, "F1-Score": f1})

    # Confusion matrix
    cm = confusion_matrix(y_val, y_preds)
    class_names = ["No Goal", "Goal"]
    # wandb.log({
    #     "Confusion Matrix": wandb.plot.confusion_matrix(
    #         probs=None,  
    #         y_true=y_val.tolist(),
    #         preds=y_preds.tolist(),
    #         class_names=class_names
    #     )
    # })