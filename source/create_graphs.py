import numpy as np
from sklearn.metrics import roc_curve, roc_auc_score
from sklearn.calibration import calibration_curve
import wandb
import pandas as pd

def wandb_roc_curve(y_true, y_pred, model_name):
    """
    Creates and logs the ROC curve and AUC in WandB, including a random baseline.
    """
    # Calculate ROC curve and AUC
    fpr, tpr, _ = roc_curve(y_true, y_pred)
    auc = roc_auc_score(y_true, y_pred)

    # Random baseline
    random_fpr = np.linspace(0, 1, 100)
    random_tpr = random_fpr

    # Log ROC curve
    wandb.log({"ROC Curve": wandb.plot.line_series(
        xs=[fpr, random_fpr],
        ys=[tpr, random_tpr],
        keys=[f"{model_name} (AUC = {auc:.2f})", "Random Baseline"],
        title="ROC Curve",
        xname="False Positive Rate"
    )})

def wandb_goal_rate_vs_percentile(y_true, y_pred, model_name):
    """
    Creates and logs the goal rate as a function of probability percentile in WandB.
    """
    # Calculate percentiles and goal rates
    percentiles = np.percentile(y_pred, np.arange(0, 101, 1))
    goal_rate = [
        np.mean(y_true[y_pred >= threshold]) if np.sum(y_pred >= threshold) > 0 else 0
        for threshold in percentiles
    ]

    # Create a WandB table to log the data
    table = wandb.Table(columns=["Percentile", "Goal Rate", "Model"])
    for percentile, rate in zip(np.arange(0, 101, 1), goal_rate):
        table.add_data(percentile, rate, model_name)

    # Log the Goal Rate vs Percentile as a shared chart
    wandb.log({
        "Goal Rate vs Percentile": wandb.plot.line(
            table,
            x="Percentile",                # X-axis: Percentile
            y="Goal Rate",                 # Y-axis: Goal Rate
            stroke="Model",                # Group by model name
            title="Goal Rate vs Probability Percentile"
        )
    })

# def wandb_cumulative_goals_vs_percentile(y_true, y_pred, model_name):
#     """
#     Creates and logs the cumulative proportion of goals as a function of the probability percentile in WandB.
#     """
#     # Sort predictions and true labels
#     sorted_indices = np.argsort(y_pred)
#     sorted_y_true = np.array(y_true)[sorted_indices]

#     # Calculate cumulative goals
#     cumulative_goals = np.cumsum(sorted_y_true)
#     total_goals = y_true.sum(axis=0) if isinstance(y_true, pd.DataFrame) else np.sum(y_true)
#     if total_goals > 0:
#         cumulative_goal_proportion = cumulative_goals / total_goals
#     else:
#         cumulative_goal_proportion = np.zeros_like(cumulative_goals)


#     # Percentiles
#     percentiles = np.arange(1, len(y_pred) + 1) / len(y_pred) * 100

#     # Log Cumulative Proportion vs Percentile
#     wandb.log({"Cumulative Goals vs Percentile": wandb.plot.line_series(
#         xs=percentiles,
#         ys=[cumulative_goal_proportion],
#         keys=["Cumulative Goal Proportion"],
#         title="Cumulative Goals vs Probability Percentile",
#         xname="Percentile"
#     )})

def wandb_cumulative_goals_vs_percentile(y_true, y_pred, model_name):
    """
    Creates and logs the cumulative proportion of goals as a function of the probability percentile in WandB.
    """
    try:
        # Sort predictions and true labels
        sorted_indices = np.argsort(y_pred)
        sorted_y_true = np.array(y_true)[sorted_indices]

        # Calculate cumulative goals
        cumulative_goals = np.cumsum(sorted_y_true)

        # Ensure total_goals is a scalar
        if isinstance(y_true, (pd.DataFrame, pd.Series)):
            total_goals = y_true.sum().item()
        else:
            total_goals = np.sum(y_true)

        # Prevent ambiguity in truth value checks
        if total_goals > 0:
            cumulative_goal_proportion = cumulative_goals / total_goals
        else:
            cumulative_goal_proportion = np.zeros_like(cumulative_goals)

        # Percentiles
        percentiles = np.arange(1, len(y_pred) + 1) / len(y_pred) * 100

        # Log Cumulative Proportion vs Percentile
        wandb.log({"Cumulative Goals vs Percentile": wandb.plot.line_series(
            xs=percentiles,
            ys=[cumulative_goal_proportion],
            keys=["Cumulative Goal Proportion"],
            title="Cumulative Goals vs Probability Percentile",
            xname="Percentile"
        )})
    except Exception as e:
        # Log the error and allow the code to continue
        print(f"Error in wandb_cumulative_goals_vs_percentile: {e}")

def wandb_reliability_diagram(y_true, y_pred, model_name):
    """
    Creates and logs the reliability diagram (calibration curve) directly in WandB.
    """
    # Calculate calibration curve
    prob_true, prob_pred = calibration_curve(y_true, y_pred, n_bins=10, strategy='uniform')

    # Log Reliability Diagram
    wandb.log({"Reliability Diagram": wandb.plot.line_series(
        xs=prob_pred,
        ys=[prob_true],
        keys=["Reliability"],
        title="Reliability Diagram",
        xname="Predicted Probability"
    )})


def create_wandb_graphs(y_true, y_pred, model_name):
    """
    Creates and logs all WandB visualizations:
    - ROC Curve with AUC and Random Baseline
    - Goal Rate vs Probability Percentile
    - Reliability Diagram (Calibration Curve)
    - Cumulative Goals vs Probability Percentile
    """
    wandb_roc_curve(y_true, y_pred, model_name)
    wandb_goal_rate_vs_percentile(y_true, y_pred, model_name)
    wandb_reliability_diagram(y_true, y_pred, model_name)
    wandb_cumulative_goals_vs_percentile(y_true, y_pred, model_name)
