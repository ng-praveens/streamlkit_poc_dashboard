import os
import shutil
import streamlit as st
from bedrock_api_interaction import (
    bedrock_response,
    setup_bedrock_client,
)
from transcription import transcription_from_file
from logger_config import logger
from propmt import notes_prompt, summary_qa_prompt

# Directory for storing uploaded files
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Streamlit App
st.set_page_config(page_title="Transcription & Notes Generator", layout="wide")
st.title("Transcription & Notes Generator")

# File uploader
uploaded_file = st.file_uploader(
    "Upload a video file", type=["mp4", "mp3", "wav", "m4a"]
)

if uploaded_file:
    # Save the uploaded file
    file_path = os.path.join(UPLOAD_FOLDER, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.success("File uploaded successfully! Processing...")

    # Get number of questions from the user
    num_questions = st.number_input(
        "Number of Questions for Summary/Q&A", min_value=1, value=5
    )

    # Process the file
    try:
        st.info("Generating transcript...")
        transcript = transcription_from_file(file_path)

        st.text_area("Transcript", transcript, height=300)

        st.info("Generating notes and summary/Q&A...")
        prompt_for_notes = notes_prompt(transcript)
        prompt_for_sqa = summary_qa_prompt(transcript, num_questions)

        # Setup Bedrock client
        client = setup_bedrock_client()

        # Get responses
        notes_response = bedrock_response(prompt_for_notes, client)
        sqa_response = bedrock_response(prompt_for_sqa, client)

        # Extract data
        notes, usage_of_notes = notes_response
        sqa, usage_of_sqa = sqa_response

        # Display results
        st.subheader("Generated Notes")
        st.text_area("Notes", notes, height=300)

        st.subheader("Summary & Q&A")
        st.text_area("Summary & Q&A", sqa, height=300)

        logger.info("Processing complete!")

    except Exception as e:
        st.error(f"Error processing file: {e}")
        logger.error(f"Error: {e}")

    finally:
        # Remove the file after processing
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Removed file: {file_path}")
