import streamlit as st

# Set page config as the first Streamlit command
st.set_page_config(layout="wide")

from apps.common import AppTemplate
from mitosheet.streamlit.v1 import spreadsheet
from apps.docp_home.pdf_to_investments import get_aggregated_dataframe
import pandas as pd
import base64
import io
from copy import deepcopy
from io import BytesIO
from apps.sidf_home.logger_config import logger


def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine="xlsxwriter")
    df.to_excel(writer, index=False, sheet_name="Sheet1")
    workbook = writer.book
    worksheet = writer.sheets["Sheet1"]
    format1 = workbook.add_format({"num_format": "0.00"})
    worksheet.set_column("A:A", None, format1)
    writer.close()
    processed_data = output.getvalue()
    return processed_data


class DocParserHomePage(AppTemplate):
    def run(self):
        logger.info("Starting Document Parser Playground App")

        st.title("Document Parser Playground App")

        uploaded_files = st.file_uploader(
            "Choose PDF files", type="pdf", accept_multiple_files=True
        )

        if uploaded_files:
            try:
                logger.info(f"{len(uploaded_files)} PDFs uploaded.")
                if "has_run" not in st.session_state:
                    df_aggregated_data = get_aggregated_dataframe(uploaded_files)
                    st.session_state.data = deepcopy(df_aggregated_data)
                    st.session_state.has_run = True
                    logger.info("Data aggregation completed successfully.")

                final_dfs, code = spreadsheet(st.session_state.data)

                df_xlsx = to_excel(final_dfs["df1"])
                st.download_button(
                    label="Download Excel", data=df_xlsx, file_name="results.xlsx"
                )
                logger.info("Excel file generated and ready for download.")

            except Exception as e:
                logger.critical(f"Critical error in app execution: {e}", exc_info=True)
                st.error("An unexpected error occurred. Please check the logs.")
        else:
            st.write("Please upload PDF files to proceed.")
