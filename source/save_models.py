import joblib
import decision_tree_model

# Step 2.1: Save the model locally
model_filename = "decision_tree_model.pkl"
joblib.dump(decision_tree_model, model_filename)

print(f"Model saved locally as {model_filename}")
