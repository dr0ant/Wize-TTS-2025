import os
import torch
from TTS.api import TTS
import psycopg2
import pandas as pd
import logging

# Setup logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

class TTSProcessor:
    def __init__(self, model_name: str, db_params: dict, device: str = None):
        """
        Initializes the TTSProcessor with a specific model and database parameters.
        :param model_name: The name of the TTS model to use
        :param db_params: Dictionary with PostgreSQL connection parameters
        :param device: The device to use for processing, defaults to 'cuda' if available, else 'cpu'
        """
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")  # Assign device here
        logger.info(f"Initializing TTSProcessor with model: {model_name} and device: {self.device}")  # Now logging works correctly
        self.db_params = db_params
        self.tts = TTS(model_name).to(self.device)
        logger.info(f"TTS model {model_name} loaded successfully on device {self.device}")

    def process_text_to_speech(self, text: str, output_filename: str):
        """
        Converts text to speech and saves it as an audio file.

        :param text: The text to convert to speech
        :param output_filename: The filename for saving the audio file
        """
        try:
            logger.info(f"Converting text to speech for file: {output_filename}")
            self.tts.tts_to_file(text=text, file_path=output_filename)
            logger.info(f"Audio saved as: {output_filename}")
        except Exception as e:
            logger.error(f"Failed to process text: {e}")

    def fetch_paragraph_data_from_postgres(self):
        """
        Fetches the paragraph content from the PostgreSQL database.

        :return: A pandas DataFrame with the fetched paragraph content
        """
        logger.info("Fetching paragraph data from PostgreSQL...")
        try:
            # Connect to the PostgreSQL database
            connection = psycopg2.connect(
                host=self.db_params['host'],
                port=self.db_params['port'],
                database=self.db_params['database'],
                user=self.db_params['user'],
                password=self.db_params['password']
            )
            query = """
            SELECT note_name, paragrapge_order, paragraphe_content
            FROM wizetts.paragraphes
            ORDER BY note_name, paragrapge_order;
            """
            df = pd.read_sql(query, connection)
            connection.close()
            logger.info(f"Fetched {len(df)} paragraphs from the database.")
            return df
        except Exception as e:
            logger.error(f"Failed to fetch data from PostgreSQL: {e}")
            return pd.DataFrame()  # Return an empty DataFrame in case of error

    def generate_audio_for_paragraphs(self):
        """
        Fetches paragraph content from PostgreSQL and converts each paragraph to speech.
        """
        logger.info("Starting audio generation for paragraphs...")
        # Fetch the paragraph data from PostgreSQL
        paragraph_data = self.fetch_paragraph_data_from_postgres()
        
        if paragraph_data.empty:
            logger.warning("No data fetched from the database.")
            return
        
        # Process each paragraph
        for _, row in paragraph_data.iterrows():
            text = row['paragraphe_content']
            note_name = row['note_name']
            output_filename = f"{note_name}_{row['paragrapge_order']}.wav"
            self.process_text_to_speech(text, output_filename)

import json

def main():
    # Directly specify the PostgreSQL connection parameters as a JSON object
    db_params = {
        'host': '100.72.70.102',
        'port': '5433',
        'database': 'wizecosm_NAS',
        'user': 'dr0ant',
        'password': '°889'
    }
    
    # Initialize the TTSProcessor with the model you want to use and the db_params
    tts_processor = TTSProcessor("tts_models/fr/mai/tacotron2-DDC", db_params)

    # Generate speech for each paragraph in the database
    tts_processor.generate_audio