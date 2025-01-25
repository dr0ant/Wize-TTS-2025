from TTS.api import TTS

# Load the model
tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2")

# List available speakers
print(tts.speakers)
