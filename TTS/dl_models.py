import os
import torch
from TTS.api import TTS
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

# Define the model path and models to preload
MODEL_NAMES = [
    "tts_models/fr/mai/tacotron2-DDC", 
    "tts_models/fr/mai/tacotron2-small"
]

def preload_model(model_name):
    """
    Preload the model to cache for faster access.
    :param model_name: The name of the TTS model to preload
    """
    logger.info(f"Preloading model {model_name}...")
    try:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        tts = TTS(model_name).to(device)
        logger.info(f"Model {model_name} preloaded successfully on {device}.")
    except Exception as e:
        logger.error(f"Failed to preload {model_name}: {e}")

def main():
    # Preload each model
    for model_name in MODEL_NAMES:
        preload_model(model_name)

if __name__ == "__main__":
    main()
