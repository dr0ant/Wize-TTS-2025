from dagster import job, op, In, Out
from icloud import icloud_loader
from postgres import postgres
from TTS_gtts import text_to_speech
import os
import pandas as pd
import logging
import yaml
import glob

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(asctime)s - %(message)s")
logger = logging.getLogger(__name__)

def load_config():
    """Load configuration from a YAML file."""
    logger.info("Loading configuration from YAML.")
    with open('config/conf.yaml', 'r') as file:
        config = yaml.safe_load(file)
    logger.info("Configuration loaded successfully.")
    return config

@op(out={"result": Out()})
def test_postgres_connection(context):
    """Step 2: Test connection to PostgreSQL."""
    logger.info("Testing PostgreSQL connection.")
    config = load_config()
    postgres_client = postgres.PostgresClient(
        host=config['postgresql']['host'],
        port=config['postgresql']['port'],
        database=config['postgresql']['database'],
        user=config['postgresql']['user'],
        password=config['postgresql']['password']
    )
    query = "SELECT 1;"
    result = postgres_client.execute_query(query)
    if result:
        context.log.info("PostgreSQL connection successful.")
        return "ok"
    else:
        context.log.error("PostgreSQL connection failed.")
        return "failed"

@op(out={"local_files": Out()})
def load_icloud_files(context):
    """Step 3: Load iCloud files locally."""
    logger.info("Loading files from iCloud.")
    config = load_config()  # Load the configuration
    username = config['icloud']['username']
    password = config['icloud']['password']
    
    # List of file paths to be loaded
    file_paths = [
        ['Obsidian', 'WizeCosm', '04 - Arcs', '01 - Phase 1', 'Phase 1 - les Séquelles de la guerre.md'],
        ['Obsidian', 'WizeCosm', '04 - Arcs', '02 - Phase 2', 'Phase 2 - Mia.md']
    ]
    
    local_files = []
    
    for path in file_paths:
        try:
            # Create the ICloudConnection instance with the current path
            icloud_conn = icloud_loader.ICloudConnection(username=username, password=password, drive_file=path)
            icloud_conn.load_md_files()  # Load the file from iCloud
            
            # Assuming tmp_md folder is the destination
            local_file_path = f"tmp_md/{'/'.join(path)}"
            local_files.append(local_file_path)  # Store the local path
            
            context.log.info(f"File loaded: {local_file_path}")
        except Exception as e:
            context.log.error(f"Error loading file {path}: {e}")
    
    return local_files

@op(ins={"start_signal": In()}, out={"result": Out()})
def create_postgres_table(context, start_signal):
    """Step 4: Drop the table if it exists and create it."""
    logger.info("Creating PostgreSQL table if it doesn't exist.")
    config = load_config()
    postgres_client = postgres.PostgresClient(
        host=config['postgresql']['host'],
        port=config['postgresql']['port'],
        database=config['postgresql']['database'],
        user=config['postgresql']['user'],
        password=config['postgresql']['password']
    )

    query = """
    DROP TABLE IF EXISTS wizetts.note_content;
    CREATE TABLE IF NOT EXISTS wizetts.note_content (
        note_name text,
        content_id serial PRIMARY KEY,
        content text,
        created_at timestamp default CURRENT_TIMESTAMP
    );
    
    ALTER TABLE wizetts.note_content OWNER TO dr0ant;
    
    CREATE INDEX IF NOT EXISTS idx_content_id ON wizetts.note_content(content_id);
    
    ALTER TABLE wizetts.note_content ADD CONSTRAINT note_name_unique UNIQUE (note_name);
    """
    try:
        postgres_client.execute_query(query, fetch=False)
        context.log.info("PostgreSQL table created successfully.")
        return "ok"
    except Exception as e:
        context.log.error(f"Error creating table: {e}")
        return "failed"

@op(ins={"local_files": In(), "start_signal": In()}, out={"result": Out()})
def load_files_to_postgres(context, local_files, start_signal):
    """Step 5: Load files into PostgreSQL."""
    logger.info("Loading files to PostgreSQL.")
    config = load_config()
    postgres_client = postgres.PostgresClient(
        host=config['postgresql']['host'],
        port=config['postgresql']['port'],
        database=config['postgresql']['database'],
        user=config['postgresql']['user'],
        password=config['postgresql']['password']
    )

    try:
        for file_path in local_files:
            # Extract just the file name from the full path
            file_name = os.path.basename(file_path)
            local_file_path = os.path.join("tmp_md", file_name)  # Full path to the file in tmp_md directory

            logger.info(f"Processing file: {local_file_path}")
            
            # Read the content of the file
            with open(local_file_path, 'r') as file:
                content = file.read()

            # Create DataFrame to upsert into PostgreSQL
            df = pd.DataFrame([{'note_name': file_name, 'content': content}])

            # Insert or update into PostgreSQL
            for index, row in df.iterrows():
                query = """
                INSERT INTO wizetts.note_content (note_name, content)
                VALUES (%s, %s)
                ON CONFLICT (note_name) DO UPDATE 
                SET content = EXCLUDED.content;
                """
                postgres_client.execute_query(query, params=(row['note_name'], row['content']), fetch=False)

            context.log.info(f"Successfully upserted file {file_name}.")
        return "ok"
    except Exception as e:
        context.log.error(f"Error processing file {file_path}: {e}")
        return "failed"

@op(ins={"start_signal": In()}, out={"result": Out()})
def delete_tmp_md(context, start_signal):
    """Step 6: Delete the tmp_md folder."""
    logger.info("Deleting tmp_md folder.")
    
    try:
        # Log the current working directory
        current_dir = os.getcwd()
        context.log.info(f"Current working directory: {current_dir}")
        
        # Identify the path of tmp_md folder
        tmp_md_path = os.path.join(current_dir, 'tmp_md')
        context.log.info(f"Path to tmp_md folder: {tmp_md_path}")

        if not os.path.exists(tmp_md_path):
            context.log.error(f"tmp_md folder does not exist at path: {tmp_md_path}")
            return "failed"
        
        # List contents of the tmp_md directory
        context.log.info(f"Contents of tmp_md folder: {os.listdir(tmp_md_path)}")
        
        # Delete all .md files in tmp_md folder
        md_files = glob.glob(os.path.join(tmp_md_path, '*.md'))
        for file in md_files:
            try:
                os.remove(file)
                context.log.info(f"Deleted file: {file}")
            except Exception as e:
                context.log.error(f"Failed to delete file {file}: {e}")

        # Now, remove the tmp_md directory itself (if empty)
        os.rmdir(tmp_md_path)
        context.log.info("Deleted tmp_md folder successfully.")
        return "ok"

    except Exception as e:
        context.log.error(f"Failed to delete tmp_md folder: {e}")
        return "failed"

@op(ins={"start_signal": In()}, out={"result": Out()})
def launch_dbt_model(context, start_signal):
    """Step 7: Launch the dbt model."""
    logger.info("Launching dbt model...")
    try:
        # Provide the full path to the dbt project directory in the command
        dbt_dir = 'wize_tts_dbt'  # Replace with the actual path to your dbt directory
        os.system(f"cd {dbt_dir} && dbt run")
        
        context.log.info("DBT model launched successfully.")
        return "ok"
    except Exception as e:
        context.log.error(f"Error launching DBT model: {e}")
        return "failed"

@op(ins={"start_signal": In()})
def generate_audio(context, start_signal):
    """Step 8: Generate audio from text and save it as an MP3 file."""
    logger.info("Generating audio from text.")
    config = load_config()
    db_params = {
        "host": config['postgresql']['host'],
        "port": config['postgresql']['port'],
        "database": config['postgresql']['database'],
        "user": config['postgresql']['user'],
        "password": config['postgresql']['password']
    }
    output_dir = "generated_audio"
    processor = text_to_speech.TTSProcessor(
        db_params=db_params,
        output_dir=output_dir
    )
    processor.generate_audio_for_paragraphs()

@job
def dagster_flow():
    """Main Dagster flow combining all steps."""
    logger.info("Starting Dagster flow.")
    
    # Define the sequential execution of operations
    local_files = load_icloud_files()
    conn_result = test_postgres_connection()
    create_table_result = create_postgres_table(start_signal=conn_result)
    loaded_files_result = load_files_to_postgres(local_files, start_signal=create_table_result)
    delete_tmp_md_result = delete_tmp_md(start_signal=loaded_files_result)
    dbt_launched_result = launch_dbt_model(start_signal=delete_tmp_md_result)
    generate_audio(start_signal=dbt_launched_result)
    
    logger.info("Dagster flow completed.")
