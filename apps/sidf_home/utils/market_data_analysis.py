from tempfile import NamedTemporaryFile
import pandas as pd
from apps.sidf_home.logger_config import logger
from .prompt import PromptReader
import os
from concurrent.futures import ThreadPoolExecutor


class ProcessmarketAnalysis:
    def __init__(self, market_data_uploaded, docx_text_data, bedrock_client):
        self.market_data_uploaded = market_data_uploaded  # UploadedFile from Streamlit
        self.docx_text_data = docx_text_data
        self.bedrock_client = bedrock_client
        self.model_id = "anthropic.claude-3-5-sonnet-20240620-v1:0"

    def process_market_data_file(self):
        # Determine file type and convert to images
        file_name = self.market_data_uploaded.name.lower()
        file_extension = os.path.splitext(file_name)[1]
        # print("uploaded market data file name----: ", file_name)
        with NamedTemporaryFile(
            delete=False, suffix=file_extension
        ) as temp_market_file:
            temp_market_file.write(self.market_data_uploaded.read())
            temp_market_file_path = temp_market_file.name
            logger.info(
                f"saved uploaded market data file in temp -: {temp_market_file_path}"
            )

        if temp_market_file_path.endswith(".xlsx"):
            market_data = pd.read_excel(file_name)
            return market_data
        elif temp_market_file_path.endswith(".csv"):
            market_data = pd.read_csv(file_name)
            return market_data
        else:
            raise ValueError("Unsupported file type. Please upload a PDF or DOCX file.")

    def extract_market_analysis(self, market_data_report, docx_text_data):
        # market_data = self.process_market_data_file()
        # Read the prompt
        pr = PromptReader("apps/sidf_home/prompts/market_analysis_prompt.txt")
        prompt_in_file = pr.read_prompt()
        final_prompt = prompt_in_file.replace("{market_data}", market_data_report)
        # print(final_prompt)
        maket_analysis_response = self.bedrock_client.get_response_text(
            final_prompt, docx_text_data, model_id=self.model_id
        )
        response_data = {"market_analysis_result": maket_analysis_response}
        return response_data
