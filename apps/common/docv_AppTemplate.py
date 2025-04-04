from abc import ABC, abstractmethod
import streamlit as st
from apps.common import Loader, Loaders
from apps.sidf_home.logger_config import logger


class AppTemplate(ABC):
    """
    This is a template class that Streamlit applications can inherit from that automatically structures them for use in a Multi-page application.
    """

    def __init__(
        self,
        title=None,
        subtitle=None,
        group=None,
        params=None,
        home_app="",
        debug=False,
        in_development=False,
        show_sidebar=True,
        parent=None,
        **kwargs,
    ):
        self.title = title
        self.subtitle = subtitle
        self.group = group
        self.in_development = in_development
        self.show_sidebar = show_sidebar
        self.home_app = home_app

        if params:
            self.app_params = params["apps"].get(title, {})
            self.app_params = params["apps"].get(subtitle, {})
            self.general_params = params.get("general", {})
        else:
            self.app_params = {}
            self.general_params = {}

        self.parent = parent
        self.debug = debug
        self.__dict__.update(kwargs)

    def load(self):
        try:
            st.query_params.page = self.title
            with st.empty().container():
                _left, _centre, _right = st.columns([2, 10, 2])
                with _left:
                    if self.title != self.home_app:
                        st.html(
                            """<a href="/?page={}&monitoring={}" target="_parent">{} Home</a>""".format(
                                self.home_app, self.group, self.group.upper()
                            )
                        )

                with _right:
                    st.html("""<a href="/" target="_parent">Monitors Home</a>""")

                if self.debug:
                    st.subheader("Session state inspector")
                    st.write(dict(st.session_state))

                self.run()

        except Exception as e:
            logger.error(f"Error loading app: {e}")
            if self.debug:
                st.write(e)
            else:
                st.toast("An error has occurred, please try again.")

    @abstractmethod
    def run(self):
        raise NotImplementedError("Each page must implement a `run` method.")
