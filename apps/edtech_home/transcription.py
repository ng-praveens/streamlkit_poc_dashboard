import whisper
import time
from logger_config import logger
import os
import pdfplumber


async def transcribe_audio_with_whisper(
    file_path: str, model_size: str = "base", device="cuda"
):
    """
    Loads a Whisper model, transcribes audio from a file, and logs performance metrics.

    Args:
        file_path (str): Path to the audio file for transcription.
        model_size (str, optional): Size of the Whisper model to load (default is "base").

    Returns:
        str: Transcribed text from the audio file.

    Raises:
        Exception: If any error occurs during model loading or transcription.
    """
    try:
        # Measure model load time
        start_time = time.perf_counter()
        model = whisper.load_model(model_size, device=device)
        end_time = time.perf_counter()
        model_load_time = end_time - start_time
        logger.info(f"Model load time: {model_load_time:.4f} seconds")

        # Measure transcription time
        start_time = time.perf_counter()
        transcript = model.transcribe(file_path)
        end_time = time.perf_counter()
        transcription_time = end_time - start_time
        logger.info(f"Transcription time: {transcription_time:.4f} seconds")
        transcript_text = transcript["text"]
        logger.info("Transcript text extracted from file.")

        return transcript_text

    except Exception as e:
        logger.error(f"Error occurred: {str(e)}", exc_info=True)
        raise


async def transcribe_from_pdf(file_path: str, file_extension: str):
    """
    Extracts text from a PDF file and logs the transcript.

    Args:
        file_path (str): Path to the PDF file for transcription.

    Returns:
        str: Extracted text from the PDF file.

    Raises:
        Exception: If any error occurs during text extraction.
    """
    if file_extension == ".pdf":
        try:
            text = ""
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() + "\n"
            logger.info("Text extracted from file")

        except Exception as e:
            logger.error(
                f"Error occurred while extracting text from {file_path}: {str(e)}",
                exc_info=True,
            )
            raise
    else:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
            logger.info("text from .txt file")

        except Exception as e:
            logger.error(
                f"Error occurred while extracting text from {file_path}: {str(e)}",
                exc_info=True,
            )
            raise
    return text


async def transcription_from_file(file_path: str):
    """
    Extracts text/transcript from a file and logs the text/transcript.

    Args:
        file_path (str): Path to the PDF file for transcription.

    Returns:
        str: Extracted text from the file.

    Raises:
        Exception: If any error occurs during text extraction.
    """

    file_extension = os.path.splitext(file_path)[1]
    if file_extension in [".pdf", ".txt"]:
        transcript = await transcribe_from_pdf(file_path, file_extension)

    else:
        transcript = await transcribe_audio_with_whisper(file_path)

    return transcript
