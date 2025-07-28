# round1b/download_model.py

from sentence_transformers import SentenceTransformer
import os

# Define the model name and the path to save it
model_name = 'all-MiniLM-L6-v2'
save_path = os.path.join(os.path.dirname(__file__), 'model')

# Create the save directory if it doesn't exist
os.makedirs(save_path, exist_ok=True)

print(f"Downloading model '{model_name}' to '{save_path}'...")

# Download the model and save it to the specified path
model = SentenceTransformer(model_name)
model.save(save_path)

print("Model download complete.")