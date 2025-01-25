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
    def __init__(self, model_name: str, db_params: dict, output_dir: str, device: str = "cpu", speaker: str = None):
        """
        Initializes the TTSProcessor with a specific model, database parameters, and output directory.
        :param model_name: The name of the TTS model to use
        :param db_params: Dictionary with PostgreSQL connection parameters
        :param output_dir: Directory to save the generated audio files
        :param device: The device to use for processing, defaults to 'cpu' (no GPU)
        :param speaker: The speaker to use for the TTS model (if applicable)
        """
        self.device = device
        logger.info(f"Initializing TTSProcessor with model: {model_name}, device: {self.device}, speaker: {speaker}")
        self.db_params = db_params
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)  # Ensure the output directory exists
        
        # Initialize TTS model using the specified model name
        self.tts = TTS(model_name)
        self.tts.to(self.device)  # Load the model onto the correct device (CPU in this case)

        self.speaker = speaker
        logger.info(f"TTS model {model_name} loaded successfully on device {self.device}")

    def process_text_to_speech(self, text: str, output_filename: str):
        """
        Converts text to speech and saves it as an audio file.

        :param text: The text to convert to speech
        :param output_filename: The filename for saving the audio file
        """
        try:
            logger.info(f"Converting text to speech for file: {output_filename}")
            file_path = os.path.join(self.output_dir, output_filename)

            # Generate speech using the speaker if provided
            self.tts.tts_to_file(
                text=text,
                file_path=file_path,
                speaker=self.speaker,  # Specify the speaker
                language="en",  # Assuming English language; adjust as needed
                split_sentences=True
            )

            logger.info(f"Audio saved as: {file_path}")
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
            SELECT note_name, paragrapge_order, content AS paragraphe_content
            FROM wizetts.cleaned_paragraphes
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
            order = row['paragrapge_order']
            output_filename = f"{note_name}_{order}.wav"
            self.process_text_to_speech(text, output_filename)


if __name__ == "__main__":
    # PostgreSQL connection parameters
    db_params = {
        "host": "100.72.70.102",  # Replace with your host
        "port": "5433",           # Replace with your port
        "database": "wizecosm_NAS",
        "user": "dr0ant",
        "password": "°889"
    }

    # Specify the speaker (if applicable)
    speaker_name = "Xavier Hayasaka"  # Replace with your desired speaker name

    # Initialize TTSProcessor
    processor = TTSProcessor(
        model_name="tts_models/multilingual/multi-dataset/xtts_v2",
        db_params=db_params,
        output_dir="generated_audio",  # Directory to save audio files
        speaker=speaker_name
    )

    # Generate audio for all paragraphs
    processor.generate_audio_for_paragraphs()
