import os
import logging
from postgres import PostgresClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LoadDocuments:
    db_client = PostgresClient(
        host="100.72.70.102",
        port="5433",
        database="wizecosm_NAS",
        user="dr0ant",
        password="°889"
    )

    def __init__(self, icloud_base_path):
        self.icloud_base_path = icloud_base_path
        if not self.icloud_base_path:
            raise ValueError("iCloud base path not set. Please provide a valid path.")
        logger.info("Initialized LoadDocuments with iCloud base path: %s", self.icloud_base_path)

    def get_note_list(self):
        select_query = "SELECT note_id, \"index\", note_path FROM wizecosm.notes_to_summarize ORDER BY \"index\";"
        results = LoadDocuments.db_client.execute_query(select_query)
        logger.info("Successfully fetched query results: %d entries found", len(results))
        return results

    def get_full_note_path(self, relative_path):
        full_path = os.path.join(self.icloud_base_path, relative_path)
        full_path = os.path.normpath(full_path)
        return full_path
