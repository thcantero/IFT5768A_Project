import wandb

sweep_config = {
    "method": "grid",
    "metric": {"name": "AUC", "goal": "maximize"},
    "parameters": {
        "learning_rate": {"values": [0.01, 0.05, 0.1]},
        "max_depth": {"values": [4, 6, 8]},
        "n_estimators": {"values": [100, 150, 200]},
    },
}

def train_xgboost():
    with wandb.init() as run:
        config = run.config
        import pandas as pd
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import roc_auc_score
        import xgboost as xgb

        data = pd.read_csv("preprocessed_data.csv")
        X = data.drop(columns=['isGoal'])
        y = data['isGoal']
        X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

        model = xgb.XGBClassifier(
            learning_rate=config.learning_rate,
            max_depth=config.max_depth,
            n_estimators=config.n_estimators
        )
        model.fit(X_train, y_train)
        y_pred = model.predict_proba(X_val)[:, 1]
        auc = roc_auc_score(y_val, y_pred)
        wandb.log({"AUC": auc})

if __name__ == "__main__":
    sweep_id = wandb.sweep(sweep_config, project="xG-best-model")
    wandb.agent(sweep_id, function=train_xgboost)
