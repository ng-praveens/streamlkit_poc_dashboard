from apps.common import AppTemplate
import streamlit as st


class EdtechHomePage(AppTemplate):
    def run(self):
        st.title("EdTech Playground App")

        ec2_url = "http://54.205.234.97:8501"  # Replace with actual EC2 URL
        monitor_home_url = "http://localhost:8501/"  # Replace with your home page URL

        # JavaScript to open EC2 URL in a new tab
        st.markdown(
            f'<a href="{ec2_url}" target="_blank"><button>Click here to open edtech app</button></a>',
            unsafe_allow_html=True,
        )
