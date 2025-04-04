from tempfile import NamedTemporaryFile
from PIL import ImageFile
from .prompt import PromptReader
from concurrent.futures import ThreadPoolExecutor
from apps.sidf_home.logger_config import logger
import pandas as pd
from docling.document_converter import DocumentConverter
from dotenv import load_dotenv

load_dotenv()

ImageFile.LOAD_TRUNCATED_IMAGES = True  # Allow loading of truncated images
IMAGE_MINE_TYPE = "image/jpeg"


class ProcessDoc:
    def __init__(self, docx_file, market_data_file, bedrock_client):
        self.market_data_file = market_data_file
        self.docx_file = docx_file
        self.bedrock_client = bedrock_client
        self.model_id = "anthropic.claude-3-5-sonnet-20240620-v1:0"

    @staticmethod
    def convert_docx_to_text(docx_file):
        """Extract text and metadata from a DOCX or PDF file using docling."""
        # Save the uploaded file temporarily
        file_extension = docx_file.name.split(".")[-1].lower()
        with NamedTemporaryFile(delete=False, suffix=f".{file_extension}") as temp_file:
            temp_file.write(docx_file.read())
            temp_file_path = temp_file.name
            logger.info(f"Saved uploaded file in temp: {temp_file_path}")

        try:
            # Use docling to extract text and metadata
            docx_data_from_docling = ProcessDoc.extract_text_with_docling(
                temp_file_path
            )
            logger.info(
                f"Successfully extracted text and metadata from {file_extension.upper()} file."
            )
        except Exception as e:
            logger.error(
                f"Error extracting text from {file_extension.upper()} file using docling: {e}"
            )
            docx_data_from_docling = None

        return {"docx_text_docling": docx_data_from_docling}

    def process_files_data(self):
        # Determine file type and convert to images
        file_name = self.docx_file.name
        logger.info(f"uploaded file loan application name----: {file_name}")
        if file_name.endswith((".pdf", ".docx")):
            images = self.convert_docx_to_text(self.docx_file)
            return images

        else:
            raise ValueError("Unsupported file type. Please upload a PDF or DOCX file.")

    @staticmethod
    def extract_text_with_docling(docx_path):
        converter = DocumentConverter()
        result = converter.convert(docx_path)
        markdown_output = result.document.export_to_markdown()
        # Ensure Markdown is UTF-8 encoded
        encoded_output = markdown_output.encode("utf-8")
        decoded_output = encoded_output.decode("utf-8")
        return decoded_output

    def data_generation(self, docx_text_data):
        pr = PromptReader("apps/sidf_home/prompts/data_generation.txt")
        prompt_data_generation = pr.read_prompt()
        data_generated = self.bedrock_client.get_response_text(
            prompt_data_generation, docx_text_data, model_id=self.model_id
        )
        # logger.info(f"result from sonnet for inconsistent data: {data_generated}")
        return data_generated

    def cl_ir_number_from_loan(self, docx_text_data):
        pr = PromptReader("apps/sidf_home/prompts/cr_il_from_text.txt")
        prompt_cl_ir_number_from_loan = pr.read_prompt()
        cl_ir_number_from_loan = self.bedrock_client.get_response_text(
            prompt_cl_ir_number_from_loan, docx_text_data, model_id=self.model_id
        )
        # logger.info(f"result from sonnet for cl_ir_number_from_loan: {cl_ir_number_from_loan}")
        return cl_ir_number_from_loan

    def process_inconsistent_data(self, docx_text_data):
        pr = PromptReader("apps/sidf_home/prompts/inconsistent_prompt.txt")
        prompt_inconsistent_data = pr.read_prompt()
        logger.info("read propmt from prompts/inconsistent_prompt.txt")

        # Get the response from the model
        incs_data = self.bedrock_client.get_response_text(
            prompt_inconsistent_data, docx_text_data, model_id=self.model_id
        )
        # logger.info(f"result from sonnet for inconsistent data: {incs_data}")
        return incs_data

    def incomplete_information(self, docx_text_data):
        pr = PromptReader("apps/sidf_home/prompts/incomplete_info.txt")
        prompt_inconsistent_data = pr.read_prompt()
        logger.info("read propmt from prompts/incomplete_info.txt")

        # Get the response from the model
        incomplete_info = self.bedrock_client.get_response_text(
            prompt_inconsistent_data, docx_text_data, model_id=self.model_id
        )
        # logger.info(f"result from sonnet for inconsistent data: {incomplete_info}")
        return incomplete_info

    def file_processor(self):
        data = ProcessDoc.process_files_data(self)

        with ThreadPoolExecutor() as executor:
            future_resp_1 = executor.submit(
                self.process_inconsistent_data, data["docx_text_docling"]
            )
            future_resp_2 = executor.submit(
                self.incomplete_information, data["docx_text_docling"]
            )
            future_resp_3 = executor.submit(
                self.data_generation, data["docx_text_docling"]
            )

            future_resp_4 = executor.submit(
                self.cl_ir_number_from_loan, data["docx_text_docling"]
            )

            inconsistent_data = future_resp_1.result()
            incomplete_info = future_resp_2.result()
            generated_data = future_resp_3.result()
            cr_il_from_loan_result = future_resp_4.result()

        final_result = {
            "inc_data": inconsistent_data,
            "incomplete_info": incomplete_info,
            "generated_data": generated_data,
            "images_extracted_data": data["docx_text_docling"],
            "cr_il_from_loan": cr_il_from_loan_result,
        }
        # logger.info(f"IL,CR,missing data, inconsistent data, incomplete info: {final_result}")
        return final_result
