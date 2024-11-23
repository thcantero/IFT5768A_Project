from sklearn.tree import DecisionTreeClassifier
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
import joblib
import wandb


# Initialize WandB
wandb.init(project="decision_tree_project", job_type="model_logging")

# Generate synthetic data
X, y = make_classification(n_samples=1000, n_features=49, random_state=42)

# Split data into training and validation sets
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

# Train the Decision Tree model
decision_tree_model = DecisionTreeClassifier(max_depth=10, random_state=42)
decision_tree_model.fit(X_train, y_train)
print("Model trained successfully!")

# Save the model locally
model_filename = "decision_tree_model.pkl"
joblib.dump(decision_tree_model, model_filename)
print(f"Model saved successfully to {model_filename}.")

# Log the model to WandB
artifact = wandb.Artifact("decision_tree_model", type="model")
artifact.add_file(model_filename)
wandb.log_artifact(artifact)
print("Model logged to WandB successfully!")

