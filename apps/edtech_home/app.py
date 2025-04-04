import streamlit as st
from st_pages import add_page_title, get_nav_from_toml
from logger_config import logger
import os


def configure_page():
    """
    Configures the Streamlit page settings.

    Sets the layout of the Streamlit page to wide and logs the action.
    """
    try:
        st.set_page_config(layout="wide")
        logger.info("Page configured successfully.")
    except Exception as e:
        logger.error(f"Error configuring the page: {e}")
        raise


def get_navigation(nav_path: str):
    """
    Loads the navigation configuration from a TOML file.

    Checks if the specified navigation configuration file exists and loads it.

    Args:
        nav_path (str): The path to the navigation configuration file.

    Returns:
        dict: The navigation configuration if loaded successfully, None otherwise.
    """
    if not os.path.exists(nav_path):
        logger.error(f"Navigation file not found: {nav_path}")
        st.error("Navigation configuration file not found.")
        return None
    try:
        nav = get_nav_from_toml(nav_path)
        logger.info("Navigation loaded successfully.")
        return nav
    except Exception as e:
        logger.error(f"Error loading navigation: {e}")
        st.error("An error occurred while loading the navigation.")
        return None


def run_page(nav):
    """
    Runs the Streamlit page based on the provided navigation configuration.

    Adds the page title and runs the page, logging the action.

    Args:
        nav (dict): The navigation configuration for the Streamlit page.
    """
    try:
        page = st.navigation(nav)
        add_page_title(page)
        page.run()
        logger.info("Page run successfully.")
    except Exception as e:
        logger.error(f"Error running the page: {e}")
        st.error("An error occurred while running the page.")
        raise


def main():
    """
    The main function to configure the page, load navigation, and run the page.

    Configures the Streamlit page settings, checks for the navigation configuration file,
    and runs the page if the navigation configuration is loaded successfully.
    """
    configure_page()  # Configures the Streamlit page settings.
    nav_path = "apps/edtech_home/.streamlit/pages.toml"
    nav = get_navigation(
        nav_path
    )  # Loads the navigation configuration from a TOML file.
    if nav:
        run_page(
            nav
        )  # Runs the Streamlit page based on the provided navigation configuration.


if __name__ == "__main__":
    main()
