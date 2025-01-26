# Notes Integration and AI Speech Generation

This project integrates notes from iCloud Storage into a PostgreSQL database, parses the notes into paragraphs using dbt models, and generates speech for each paragraph using AI-powered Text-to-Speech (TTS).

## Overview

The main goal of this project is to automate the following processes:
1. **Integrating Notes from iCloud Storage:** Extract notes stored on iCloud and store them in a PostgreSQL table for further processing.
2. **Parsing Paragraphs:** Use dbt models to process and organize the content of the notes into individual paragraphs for easier manipulation.
3. **AI TTS Speech Generation:** Convert the parsed paragraphs into speech using AI-powered TTS technology.

## Project Structure

### 1. iCloud Storage Integration

- **Objective:** Retrieve notes from iCloud Storage and insert them into a PostgreSQL table.
- **Tools:** Python, iCloud API (or equivalent)
- **Details:**
    - Authenticate with iCloud storage to retrieve stored notes.
    - Parse the content of the notes into a suitable format (e.g., JSON or text).
    - Insert the parsed notes into a PostgreSQL table, where each note is stored with its relevant metadata (e.g., title, creation date, etc.).

### 2. dbt Model for Paragraph Parsing

- **Objective:** Use dbt to parse and structure the note content into paragraphs.
- **Tools:** dbt (data build tool), PostgreSQL
- **Details:**
    - Create dbt models to process the notes stored in the PostgreSQL table.
    - Split the content of each note into paragraphs using text functions (e.g., splitting by newlines or sentence length).
    - Organize the parsed paragraphs into a new table or model that can be queried for speech generation.

### 3. AI Text-to-Speech (TTS) Speech Generation

- **Objective:** Convert the parsed paragraphs into AI-generated speech.
- **Tools:** Python, AI TTS (e.g., Google Cloud Text-to-Speech, Amazon Polly, or any other suitable TTS service)
- **Details:**
    - Retrieve each paragraph from the dbt model.
    - Use AI TTS to generate speech from each paragraph.
    - Store the resulting speech files (e.g., MP3) or play them directly.

## Setup and Installation

### Prerequisites

- Python 3.10+
- PostgreSQL database
- dbt setup (for model processing)
- TTS API credentials (Google Cloud, Amazon Polly, etc.)

### Steps to Set Up

1. **Clone the Repository:**
    ```bash
    git clone <repository-url>
    cd <repository-folder>
    ```

2. **Install Python Dependencies:**
    Create a virtual environment and install the required Python packages.
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

3. **Set Up PostgreSQL Database:**
    - Create a PostgreSQL database and user.
    - Import the schema for storing notes and parsed paragraphs.

4. **Configure iCloud Integration:**
    - Set up iCloud API credentials or other necessary configurations for accessing iCloud storage.

5. **Configure dbt:**
    - Set up dbt with the appropriate PostgreSQL connection settings.
    - Run dbt models to parse and structure the notes.

6. **Set Up TTS API:**
    - Set up an AI TTS service (Google Cloud, Amazon Polly, etc.).
    - Configure the TTS API credentials in the project.

### Running the Project

1. **Integrate Notes into PostgreSQL:**
    Run the Python script to fetch notes from iCloud and insert them into the PostgreSQL table.
    ```bash
    python integrate_notes.py
    ```

2. **Run dbt Models:**
    Run dbt to parse and process the notes into paragraphs.
    ```bash
    dbt run
    ```

3. **Generate Speeches:**
    link to TTS doc : https://docs.coqui.ai/en/latest/models/xtts.html


    Run the Python script to generate speech for each paragraph using the TTS API.
    ```bash
    python generate_speech.py
    ```

## Project Workflow

1. Fetch notes from iCloud Storage.
2. Insert notes into PostgreSQL.
3. Use dbt to parse the notes into individual paragraphs.
4. For each paragraph, use AI TTS to create a speech file (e.g., MP3).
5. Optionally, play or store the generated speech files.

## Future Improvemen