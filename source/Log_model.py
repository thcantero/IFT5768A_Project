import wandb

# Step 4.1: Initialize WandB
wandb.init(project="decision_tree_project", job_type="model_logging")

# Step 4.2: Create a WandB artifact
artifact = wandb.Artifact("decision_tree_model", type="model")

# Step 4.3: Add the model and script to the artifact
artifact.add_file(model_filename)  # Add the model
artifact.add_file(script_filename)  # Add the script

# Step 4.4: Log the artifact
wandb.log_artifact(artifact)

print("Model and script logged to WandB successfully!")
