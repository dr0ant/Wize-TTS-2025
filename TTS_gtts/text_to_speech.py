import os
from gtts import gTTS
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
    def __init__(self, db_params: dict, output_dir: str, lang: str = 'fr'):
        """
        Initializes the TTSProcessor with database parameters and output directory.
        :param db_params: Dictionary with PostgreSQL connection parameters
        :param output_dir: Directory to save the generated audio files
        :param lang: The language of the TTS, defaults to 'fr' (French)
        """
        self.lang = lang
        logger.info(f"Initializing TTSProcessor with language: {self.lang}")
        self.db_params = db_params
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)  # Ensure the output directory exists

    def process_text_to_speech(self, text: str, output_filename: str):
        """
        Converts text to speech and saves it as an audio file.
        :param text: The text to convert to speech
        :param output_filename: The filename for saving the audio file
        """
        try:
            logger.info(f"Converting text to speech for file: {output_filename}")
            file_path = os.path.join(self.output_dir, output_filename)

            tts = gTTS(text=text, lang=self.lang)
            tts.save(file_path)

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
            output_filename = f"{note_name}_{order}.mp3"
            self.process_text_to_speech(text, output_filename)


