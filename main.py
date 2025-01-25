import torch
import sys
import os
import sys
import os
import pprint 
from TTS.api import TTS
from load_text import  LoadDocuments
import torch
import os
from TTS.api import TTS
from load_text import LoadDocuments

# Get device
device = "cuda" if torch.cuda.is_available() else "cpu"

# Initialize a model that has pre-trained speakers
tts = TTS("tts_models/fr/mai/tacotron2-DDC").to(device)

# Initialize the class with the iCloud base path directly
load_documents = LoadDocuments(icloud_base_path='/Users/antoinelarcher/Library/Mobile Documents/iCloud~md~obsidian/Documents')

# Fetch note list and process
note_list = load_documents.get_note_list()

# Process each note and convert to audio
for note_id, index, relative_path in note_list:
    full_note_path = load_documents.get_full_note_path(relative_path)
    
    if not os.path.exists(full_note_path):
        continue

    try:
        with open(full_note_path, 'r', encoding='utf-8') as f:
            md_content = f.read()  # Read entire content

        # Get the filename for the output audio (based on the last part of the file path)
        output_filename = os.path.basename(full_note_path).replace('.md', '.wav')
        
        # Generate the audio file using TTS
        tts.tts_to_file(text=md_content, file_path=output_filename)
        print(f"Audio saved as: {output_filename}")

    except Exception as e:
        print(f"Failed to process file {full_note_path}: {e}")
