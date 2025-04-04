from abc import ABC, abstractmethod
import streamlit as st
from apps.common import Loader, Loaders
import streamlit as st
from PIL import Image
import pandas as pd
import json
from concurrent.futures import ThreadPoolExecutor
from apps.sidf_home.utils.market_data_analysis import ProcessmarketAnalysis
from apps.sidf_home.llm.bedrock_client import BedrockClient
from apps.sidf_home.utils.cr_process import ProcessCR
from apps.sidf_home.utils.il_process import ProcessIL
from apps.sidf_home.utils.doc_process import ProcessDoc
import base64
import os
from dotenv import load_dotenv
from apps.sidf_home.logger_config import logger
from apps.common.docv_AppTemplate import AppTemplate

load_dotenv()


class DocumentProcessingApp(AppTemplate):
    """
    Document processing app that allows users to upload documents and process them
    (e.g., extract text, images, and handle market data analysis).
    """

    def __init__(
        self,
        title="A Streamlit application for document processing",
        subtitle="",
        group="Group 1",
        params=None,
        home_app="",
        debug=False,
        in_development=False,
        show_sidebar=True,
        parent=None,
        **kwargs,
    ):
        super().__init__(
            title,
            subtitle,
            group,
            params,
            home_app,
            debug,
            in_development,
            show_sidebar,
            parent,
            **kwargs,
        )

        # self.logo_img_path = "apps/sidf_home/static/image.png"
        # self.sidebar_img_path = "apps/sidf_home/static/logo.jpg"
        self.model_id = "anthropic.claude-3-haiku-20240307-v1:0"

    # def configure_page(self):
    #     img = Image.open(self.logo_img_path)
    #     logger.info("Page configuration set with title and icon.")

    def display_header(self):
        """Display the title and subtitle."""
        st.markdown(
            f"<h3 style='text-align:center;padding: 0px 0px;color:black;'>{self.title}</h3>"
            f"<h4 style='text-align:center;color:grey;font-size:80%;'><i>{self.subtitle}</i></h4>",
            unsafe_allow_html=True,
        )

    def apply_custom_styling(self):
        def get_img_as_base64(file_path):
            with open(file_path, "rb") as file:
                return base64.b64encode(file.read()).decode("utf-8")

        background_img = get_img_as_base64("apps/sidf_home/blue.jpg")
        page_bg_img = f"""
        <style>
        [data-testid="stAppViewContainer"] {{
        background-image: url("data:image/png;base64,{background_img}");
        background-size: 120%;
        background-repeat: no-repeat;
        background-attachment: local;
        }}
        </style>
        """
        st.markdown(page_bg_img, unsafe_allow_html=True)
        logger.info("Applied custom page styling with background image.")

    def run(self):
        # Set page config at the very start of the run method
        # self.configure_page()  # This should remain as part of the styling config
        self.apply_custom_styling()
        self.display_header()

        doc_file, industry_licence, comm_licence, market_data_file = (
            self.customize_sidebar()
        )

        bedrock_client = BedrockClient(
            aws_access_key=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        )
        logger.info("BedrockClient initialized.")

        market_data_report = None
        if market_data_file:
            market_data_report = self.extract_market_data(market_data_file)
        doc_response, cr_response, il_response = None, None, None
        (
            instructions_tab,
            document_verification_tab,
            inconsistent_data_tab,
            incomplete_data_tab,
            data_generation_tab,
            analysis_tab,
        ) = st.tabs(
            [
                "Instructions",
                "Document Verification",
                "Inconsistent Data",
                "Incomplete Information",
                "Data Generation",
                "Analysis",
            ]
        )
        with instructions_tab:
            st.markdown(
                """
                # Instructions
                This application processes loan application documents, commercial registration images, and industry license images.
                - Upload the documents and images on the sidebar.
                - Once uploaded, click the "Process" button to start processing.
                - Each tab below will show different sections of the processed data.
                """
            )

            process_button = st.button("Process", key="parse")
            if process_button:
                logger.info("Processing documents...")
                with st.spinner("Processing..."):
                    with ThreadPoolExecutor() as executor:
                        futures = {
                            "doc_response": executor.submit(
                                self.process_document,
                                doc_file,
                                market_data_file,
                                bedrock_client,
                            ),
                            "cr_response": executor.submit(
                                self.process_commercial_registration,
                                comm_licence,
                                bedrock_client,
                            ),
                            "il_response": executor.submit(
                                self.process_industry_license,
                                industry_licence,
                                bedrock_client,
                            ),
                        }

                        results = {
                            key: future.result() for key, future in futures.items()
                        }
                        doc_response = results["doc_response"]
                        cr_response = results["cr_response"]
                        il_response = results["il_response"]
                        logger.info("Completed parallel processing for all tasks.")

                        market_analysis_result = self.extract_market_analysis_response(
                            market_data_report, doc_response, bedrock_client
                        )
                        st.success("Processing completed.")

        # self.display_processed_data(doc_response, cr_response, il_response)
        with document_verification_tab:
            if doc_response is not None:
                data = doc_response.get("cr_il_from_loan")
                extracted_data = json.loads(data)
                verification_results = []
                if il_response and "resolution_number" in il_response:
                    cr_il_data = extracted_data.get("cr_il_from_loan", {})
                    industrial_license_value = cr_il_data.get(
                        "industrial_license_value"
                    )
                    il_number_from_image = il_response["resolution_number"]
                    if industrial_license_value == il_number_from_image:
                        verification_results.append(
                            {
                                "Verification Type": "Industrial License Number",
                                "Loan Application Value": industrial_license_value,
                                "Uploaded Image Value": il_number_from_image,
                                "Result": "✅ Matched",
                            }
                        )
                    else:
                        verification_results.append(
                            {
                                "Verification Type": "Industrial License Number",
                                "Loan Application Value": industrial_license_value,
                                "Uploaded Image Value": il_number_from_image,
                                "Result": "❌ Not Matched",
                            }
                        )
                else:
                    verification_results.append(
                        {
                            "Verification Type": "Industrial License Number",
                            "Loan Application Value": "N/A",
                            "Uploaded Image Value": "N/A",
                            "Result": "❌ Missing or Invalid",
                        }
                    )

                if cr_response and "establishment_number" in cr_response:
                    cr_il_data = extracted_data.get("cr_il_from_loan", {})
                    commercial_register_value = cr_il_data.get(
                        "commercial_register_value"
                    )
                    cr_number_from_image = cr_response["establishment_number"]

                    if commercial_register_value == cr_number_from_image:
                        verification_results.append(
                            {
                                "Verification Type": "Commercial Registration Number",
                                "Loan Application Value": commercial_register_value,
                                "Uploaded Image Value": cr_number_from_image,
                                "Result": "✅ Matched",
                            }
                        )
                    else:
                        verification_results.append(
                            {
                                "Verification Type": "Commercial Registration Number",
                                "Loan Application Value": commercial_register_value,
                                "Uploaded Image Value": cr_number_from_image,
                                "Result": "❌ Not Matched",
                            }
                        )
                else:
                    verification_results.append(
                        {
                            "Verification Type": "Commercial Registration Number",
                            "Loan Application Value": "N/A",
                            "Uploaded Image Value": "N/A",
                            "Result": "❌ Missing or Invalid",
                        }
                    )
                st.markdown("### Verification Results")
                if verification_results:
                    df = pd.DataFrame(verification_results)
                    st.write(df.to_html(index=False), unsafe_allow_html=True)

        # Inconsistent Data Tab
        with inconsistent_data_tab:
            if doc_response is not None:
                st.markdown(
                    "<h3 style='text-align: center;'>Inconsistent Data</h3>",
                    unsafe_allow_html=True,
                )
                inconsistent_data = doc_response.get("inc_data", {})
                st.write(inconsistent_data)
            else:
                st.write("No inconsistent data to display.")

        # Incomplete Data Tab
        with incomplete_data_tab:
            if doc_response is not None:
                st.markdown(
                    "<h3 style='text-align: center;'>Incomplete Information</h3>",
                    unsafe_allow_html=True,
                )
                incomplete_data = doc_response.get("incomplete_info", {})
                st.write("Incomplete Data:", str(incomplete_data))
            else:
                st.write("No incomplete data to display.")

        # Data Generation Tab
        with data_generation_tab:
            if doc_response is not None:
                st.markdown("### Data Generation")
                generated_data = doc_response.get("generated_data", {})
                st.write(generated_data)
            else:
                st.write("No data generation results to display.")

        with analysis_tab:
            if doc_response:

                st.markdown("### Market Data")

                st.markdown(
                    f"<div style='line-height:1.5;'>{market_analysis_result}</div>",
                    unsafe_allow_html=True,
                )
                logger.info("Displayed market analysis.")
            else:
                st.write(
                    "No document processing response available for market analysis."
                )

    def customize_sidebar(self):
        st.markdown(
            """
            <style>
                [data-testid=stSidebar] [data-testid=stImage]{
                    text-align: center;
                    display: block;
                    margin-left: auto;
                    margin-right: auto;
                    width: 100%;
                }
            </style>
            """,
            unsafe_allow_html=True,
        )

        with st.sidebar:
            # org_img = Image.open(self.sidebar_img_path)
            # st.image(org_img)
            doc_file = st.file_uploader("Upload Loan Application", type=["pdf", "docx"])
            industry_licence = st.file_uploader(
                "Upload Industry License", type=["jpg", "png"]
            )
            comm_licence = st.file_uploader(
                "Upload Commercial Registration", type=["jpg", "png"]
            )
            market_data_file = st.file_uploader("Upload Market Data", type=["csv"])

        logger.info("Sidebar customized with file upload options.")
        return doc_file, industry_licence, comm_licence, market_data_file

    def extract_market_data(self, market_data_file):
        if market_data_file:
            if market_data_file.name.endswith(".xlsx"):
                logger.info(
                    f"Extracting market data from {market_data_file.name} (xlsx)."
                )
                return pd.read_excel(market_data_file)
            elif market_data_file.name.endswith(".csv"):
                logger.info(
                    f"Extracting market data from {market_data_file.name} (csv)."
                )
                return pd.read_csv(market_data_file)
        logger.warning("No market data file uploaded.")
        return None

    def process_document(self, doc_file, market_data_file, bedrock_client):
        if doc_file:
            logger.info("Processing document...")
            doc_process = ProcessDoc(doc_file, market_data_file, bedrock_client)
            return doc_process.file_processor()
        logger.warning("No document file uploaded.")
        return None

    def process_commercial_registration(self, comm_licence, bedrock_client):
        if comm_licence:
            logger.info("Processing commercial registration document...")
            cr_processor = ProcessCR(comm_licence, bedrock_client)
            return cr_processor.process_files()
        logger.warning("No commercial registration file uploaded.")
        return None

    def process_market_analysis(self, market_data_df, docx_text_data, bedrock_client):
        if market_data_df is not None and not market_data_df.empty:
            market_analysis = ProcessmarketAnalysis(
                market_data_df, docx_text_data, bedrock_client
            )
            return market_analysis.extract_market_analysis(
                market_data_df.to_string(index=False), docx_text_data
            )
        return None

    def process_industry_license(self, industry_licence, bedrock_client):
        if industry_licence:
            logger.info("Processing industry license document...")
            il_process = ProcessIL(industry_licence, bedrock_client)
            return il_process.process_files()
        logger.warning("No industry license file uploaded.")
        return None

    def extract_market_analysis_response(
        self, market_data_report, doc_response, bedrock_client
    ):
        if market_data_report is not None and not market_data_report.empty:
            logger.info("Extracting market analysis from market data report.")
            market_analysis = self.process_market_analysis(
                market_data_report,
                doc_response.get("images_extracted_data", {}),
                bedrock_client,
            )
            market_data_to_ui = market_analysis.get("market_analysis_result", {})
            logger.info("Extracted market analysis.")
            return market_data_to_ui
        else:
            logger.warning("No market data available to analyze.")
            st.write("No market data to analyze.")

    def display_processed_data(self, doc_response, cr_response, il_response):
        # st.subheader("Processed Data")
        if doc_response:
            st.write(doc_response)
        if cr_response:
            st.write(cr_response)
        if il_response:
            st.write(il_response)
        logger.info("Displayed processed data.")


if __name__ == "__main__":
    app = DocumentProcessingApp(
        title="A Streamlit application for document processing",
        subtitle="Brought to you by AI Team",
    )
    app.load()
