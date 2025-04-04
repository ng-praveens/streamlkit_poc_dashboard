import streamlit as st
import httpx
import json
import asyncio
from logger_config import logger

st.sidebar.success("Select Any Page from here after clicking upload button")


async def httpx_response(uploaded_file, number_of_questions: int):
    """
    Handles the upload of a file, sending it to the server for processing, and storing the response in session state.

    Parameters:
    - uploaded_file: The file object that has been uploaded by the user.
    - number_of_questions: Number of questions to be processed.

    Returns:
    None
    """
    async with httpx.AsyncClient(timeout=600) as client:
        files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
        data = {"number_of_questions": str(number_of_questions)}

        response = await client.post(
            "http://localhost:8000/upload/", files=files, data=data
        )
        logger.info("Response generated from httpx.")
        # Check if the response status is 200 (OK)
        if response.status_code == 200:
            st.success("Video uploaded successfully.")

            # Parse the response data and store it in session state
            response_data = response.json()
            st.session_state["response_data"] = response_data
            st.session_state["transcript"] = response_data.get("transcript", "")

            # Load summary and questions data from the response
            data = json.loads(response_data.get("summary_qa", "{}"))
            notes = response_data.get("notes", "")
            st.session_state["data"] = data
            st.session_state["notes"] = notes
        else:
            # Display an error message if the upload fails
            st.error(f"Failed to upload video. Status code: {response.status_code}")


async def handle_upload(uploaded_file, number_of_questions: int):
    """
    Handles the upload of a file and number of questions, verify the file uploaded and storing in session state.

    Parameters:
    - uploaded_file: The file object that has been uploaded by the user.
    - number_of_questions: Number of questions to be processed.

    Returns:
    None
    """
    # Generate a unique identifier for the uploaded file based on its name and size
    file_identifier = uploaded_file.name + str(uploaded_file.size)

    # Check if a different file has been uploaded previously
    if (
        "file_identifier" in st.session_state
        and st.session_state["file_identifier"] != file_identifier
    ):
        # Clear previous response data if a new file is uploaded
        for key in ["response_data", "data", "notes", "user_answers", "transcript"]:
            st.session_state.pop(key, None)

    # Store the uploaded file and its identifier in session state
    st.session_state["uploaded_file"] = uploaded_file
    st.session_state["file_identifier"] = file_identifier
    st.session_state["number_of_questions"] = number_of_questions

    # Check if an uploaded file exists in session state
    if (
        "uploaded_file" in st.session_state
        and "number_of_questions" in st.session_state
        and "response_data" not in st.session_state
    ):
        # Retrieve the uploaded file from session state
        uploaded_file = st.session_state["uploaded_file"]
        number_of_questions = st.session_state["number_of_questions"]

        # Check if response data does not exist in session state
        try:
            # Use an asynchronous HTTP client to send the file to the server for processing
            await httpx_response(uploaded_file, number_of_questions)

        except httpx.RequestError as e:
            # Handle network errors
            st.error(f"An error occurred while uploading the file: {e}")

        except httpx.HTTPStatusError as e:
            # Handle HTTP errors
            st.error(f"HTTP error occurred: {e}")

        except json.JSONDecodeError as e:
            # Handle JSON decoding errors
            st.error(f"Error decoding response JSON: {e}")

        except Exception as e:
            # Handle any other unexpected errors
            st.error(f"An unexpected error occurred: {e}")


async def main():
    """
    The main function for the Streamlit app. It handles the video upload,
    processes the uploaded file, and displays the resulting summary, notes, and Q&A.

    Parameters:
    None

    Returns:
    None
    """
    # Title of the app
    st.title("File Upload to Summary, Notes, Q&A ")
    st.markdown(
        """
        ## Welcome to the File Upload App

        This app allows you to upload various types of files including video and text documents. 
        Once you upload a file, the app will process it and provide the following:

        - **Summary**: A summary of the content.
        - **Notes**: Important notes extracted from the content.
        - **Questions & Answers**: A set of questions and answers based on the content.

        ### How to Use:
        1. **Upload a File**: Select a file from your local system.
        2. **Set Number of Questions**: Choose how many questions you want the app to generate.
        3. **Click 'Upload'**: The app will process the file and provide results.
        4. **Click 'Notes and Summary'**: This will show the Notes and Summary.
        5. **Click 'Q&A'**: This will show the Q&A.

        **Note**: The processing might take some time depending on the size of the file.
        """
    )
    # Initialize session state variables if not already present
    if "processing" not in st.session_state:
        st.session_state["processing"] = False
    if "uploaded_file" not in st.session_state:
        st.session_state["uploaded_file"] = None
    if "number_of_questions" not in st.session_state:
        st.session_state["number_of_questions"] = 15

    # Sidebar components for file upload and settings
    with st.sidebar:
        uploaded_file = st.file_uploader(
            "Choose a video...", type=["mp4", "wav", "mp3", "avi", "mkv", "pdf", "txt"]
        )
        number_of_questions = st.slider(
            "Choose number of questions...",
            min_value=1,
            max_value=25,
            value=st.session_state["number_of_questions"],
            step=1,
        )

        if st.button("Upload") and uploaded_file is not None:
            st.session_state["uploaded_file"] = uploaded_file
            st.session_state["number_of_questions"] = number_of_questions
            st.session_state["processing"] = True

    # Main area to show processing status and results
    if st.session_state["processing"]:
        with st.spinner("Processing..."):
            # Call the handle_upload function with the uploaded file and number of questions
            await handle_upload(
                st.session_state["uploaded_file"],
                st.session_state["number_of_questions"],
            )
            st.session_state["processing"] = False

        st.success("Processing complete!")


# initializing the main() function
asyncio.run(main())
