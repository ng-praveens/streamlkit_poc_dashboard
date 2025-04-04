from apps.common.docv_AppTemplate import AppTemplate
import streamlit as st
import pandas as pd
import json
from apps.email_home.utils import load_excel, save_to_excel, generate_prompts
from apps.email_home.openai_utils import get_email_sequence
from apps.email_home.email_utils import send_emails
from apps.email_home.logger_config import logger


class PersonalizedEmailHomePage(AppTemplate):
    def run(self):
        logger.info("Application started.")

        if "step" not in st.session_state:
            st.session_state.step = 1
        if "selected_email_number" not in st.session_state:
            st.session_state.selected_email_number = "Email 1"
        if "current_email_index" not in st.session_state:
            st.session_state.current_email_index = 0
        if "row_index" not in st.session_state:
            st.session_state.row_index = 0  # Initialize to first row
        if "col_name" not in st.session_state:
            st.session_state.col_name = "email_sequence"

        if "text_area" not in st.session_state:
            st.session_state.text_area = ""  # Default empty string

        logger.info(f"Current step: {st.session_state.step}")

        # logo_url = "apps/email_home/ngenux.png"
        # st.image(logo_url, width=150)
        st.title("Personalized Email Playground App")

        if st.session_state.step == 1:
            st.header("Step 1: Upload Contacts..[Excel File]")
            uploaded_file = st.file_uploader("Choose an Excel file", type="xlsx")

            if uploaded_file:
                logger.info("Excel file uploaded.")
                try:
                    st.session_state.df = load_excel(uploaded_file)
                    st.session_state.step = 2
                    st.success("Document uploaded and data loaded successfully!")
                    st.dataframe(st.session_state.df, use_container_width=True)
                    logger.info("Excel file loaded successfully.")
                except Exception as e:
                    st.error("Error loading Excel file.")
                    logger.error(f"Error loading Excel file: {e}")

        if st.session_state.step == 2:
            if "df" in st.session_state:
                st.header("Step 2: Select Contacts")
                contact_names = st.session_state.df["contact name"].unique().tolist()
                contact_names.insert(0, "Select All")
                selected_contacts = st.multiselect(
                    "Select Contact Names", contact_names
                )

                if "Select All" in selected_contacts:
                    selected_contacts = contact_names[1:]

                st.session_state.selected_df = st.session_state.df[
                    st.session_state.df["contact name"].isin(selected_contacts)
                ].reset_index(drop=True)
                st.dataframe(st.session_state.selected_df, use_container_width=True)

                if st.button("Generate Prompts", key="generate_prompts_button"):
                    st.session_state.step = 4
                    logger.info("Contacts selected, moving to prompt generation.")

        if st.session_state.step == 4:
            if "selected_df" in st.session_state:
                st.header("Step 4: Generate Personalized Prompts")
                if st.button("Generate Prompts", key="generate_prompts_button_2"):
                    try:
                        st.session_state.selected_df = generate_prompts(
                            st.session_state.selected_df
                        )
                        st.session_state.step = 5
                        st.success("Prompts generated!")
                        st.dataframe(
                            st.session_state.selected_df, use_container_width=True
                        )
                        logger.info("Prompts generated successfully.")
                    except Exception as e:
                        st.error("Error generating prompts.")
                        logger.error(f"Error generating prompts: {e}")

        if st.session_state.step == 5:
            if "selected_df" in st.session_state:
                st.header("Step 5: Generate Emails")
                if st.button("Generate Emails", key="generate_emails_button"):
                    try:
                        st.session_state.selected_df["email_sequence"] = (
                            st.session_state.selected_df["personalized_prompt"].apply(
                                get_email_sequence
                            )
                        )
                        st.session_state.selected_email_number = "Email 1"
                        st.session_state.step = 6
                        st.success("Email sequences generated!")
                        st.dataframe(
                            st.session_state.selected_df, use_container_width=True
                        )
                        logger.info("Emails generated successfully.")
                    except Exception as e:
                        st.error("Error generating emails.")
                        logger.error(f"Error generating emails: {e}")

        def update_df():
            row_index = st.session_state.row_index
            email_data2 = json.loads(
                st.session_state.selected_df.at[row_index, st.session_state.col_name]
            )
            email_data2["Email 1"]["Body"] = st.session_state.text_area
            st.session_state.selected_df.at[row_index, st.session_state.col_name] = (
                json.dumps(email_data2)
            )
            logger.info(f"Updated email content for row {row_index}.")

        if st.session_state.step == 6:
            if "selected_df" in st.session_state:
                st.header("Step 6: Edit Emails")
                try:
                    email_data = json.loads(
                        st.session_state.selected_df.at[
                            st.session_state.row_index, st.session_state.col_name
                        ]
                    )["Email 1"]
                    st.text_area(
                        "Edit value",
                        value=email_data["Body"],
                        key="text_area",
                        on_change=update_df,
                        height=700,
                    )
                    logger.info("Loaded email for editing.")
                except Exception as e:
                    st.error("Error loading email for editing.")
                    logger.error(f"Error loading email: {e}")

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Previous Email", key="previous_email_button"):
                        if st.session_state.row_index > 0:
                            update_df()
                            st.session_state.row_index -= 1
                            st.rerun()
                        else:
                            st.warning("Already at the first row.")

                with col2:
                    if st.button("Next Email", key="next_email_button"):
                        if (
                            st.session_state.row_index
                            < len(st.session_state.selected_df) - 1
                        ):
                            update_df()
                            st.session_state.row_index += 1
                            st.rerun()
                        else:
                            st.warning("Already at the last row.")

                if st.button("Save changes", key="save_changes_button"):
                    update_df()
                    st.session_state.step = 7
                    logger.info("Email edits saved.")

        if st.session_state.step == 7:
            if "selected_df" in st.session_state:
                st.header("Step 7: Send Emails")
                if st.button("Send Emails", key="send_emails_button"):
                    save_to_excel(st.session_state.selected_df, "final_emails.xlsx")
                    try:
                        results = send_emails(st.session_state.selected_df)
                        st.success("All emails sent successfully!")
                        for result in results:
                            st.write(result)
                        logger.info("Emails sent successfully.")
                    except Exception as e:
                        st.error("Error sending emails.")
                        logger.error(f"Error sending emails: {e}")
