import os
import torch
from dagster import job, op, get_dagster_logger
from TTS.api import TTS
from load_text import LoadDocuments

# Define an op to initialize the TTS model
@op
def initialize_tts() -> TTS:
    device = "cuda" if torch.cuda.is_available() else "cpu"
    tts = TTS("tts_models/fr/mai/tacotron2-DDC").to(device)
    get_dagster_logger().info(f"TTS model initialized on device: {device}")
    return tts

# Define an op to initialize the document loader
@op
def initialize_document_loader() -> LoadDocuments:
    load_documents = LoadDocuments(icloud_base_path='/Users/antoinelarcher/Library/Mobile Documents/iCloud~md~obsidian/Documents')
    get_dagster_logger().info("Document loader initialized.")
    return load_documents

# Define an op to fetch and process notes
@op
def process_notes(load_documents: LoadDocuments, tts: TTS):
    note_list = load_documents.get_note_list()
    for note_id, index, relative_path in note_list:
        full_note_path = load_documents.get_full_note_path(relative_path)
        
        if not os.path.exists(full_note_path):
            get_dagster_logger().warning(f"File does not exist: {full_note_path}")
            continue

        try:
            with open(full_note_path, 'r', encoding='utf-8') as f:
                md_content = f.read()

            # Get the output filename
            output_filename = os.path.basename(full_note_path).replace('.md', '.wav')

            # Generate the audio file
            tts.tts_to_file(text=md_content, file_path=output_filename)
            get_dagster_logger().info(f"Audio saved as: {output_filename}")

        except Exception as e:
            get_dagster_logger().error(f"Failed to process file {full_note_path}: {e}")

# Define the Dagster job
@job
def tts_conversion_job():
    tts = initialize_tts()
    load_documents = initialize_document_loader()
    process_notes(load_documents, tts)
