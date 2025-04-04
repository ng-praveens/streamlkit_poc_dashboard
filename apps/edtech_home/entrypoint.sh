#!/bin/bash

# Start the FastAPI application in the background
uvicorn file_processing:app --host 0.0.0.0 --port 8000 &

# Start the Streamlit application
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
