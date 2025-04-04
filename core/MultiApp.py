from abc import ABC
import streamlit as st
from typing import Dict, Type
from apps import AppTemplate


HIDE_ST_STYLE = """
                <style>
div[data-testid="stToolbar"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }
                div[data-testid="stDecoration"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }
                #MainMenu {
                visibility: hidden;
                height: 0%;
                }
                header {
                visibility: hidden;
                height: 0%;
                }
                footer {
                visibility: hidden;
                height: 0%;
                }
				        .appview-container .main .block-container{
                            padding-top: 0rem;
                            padding-right: 3rem;
                            padding-left: 3rem;
                            padding-bottom: 0rem;
                        }  
                        .appview-container .sidebar-content {
                            padding-top: 0rem;
                        }
                        .reportview-container {
                            padding-top: 0rem;
                            padding-right: 3rem;
                            padding-left: 3rem;
                            padding-bottom: 0rem;
                        }
                        .reportview-container .sidebar-content {
                            padding-top: 0rem;
                        }
                        header[data-testid="stHeader"] {
                            z-index: -1;
                        }
                        div[data-testid="stToolbar"] {
                        z-index: 100;
                        }
                        div[data-testid="stDecoration"] {
                        z-index: 100;
                        }
                        .reportview-container .sidebar-content {
                            padding-top: 0rem;
                        }
                        div[data-stale="false"] > iframe[title="hydralit_components.NavBar.nav_bar"] {
                        z-index: 99;
                    }
                </style>
                """


class MultiPageApp(ABC):
    def __init__(self, name, hide_st_stuff = True, group_parent=None,debug=False,in_development=False, **kwargs):
        self.pages: Dict[str, Type[AppTemplate]] = {}
        self.hiddenpages: Dict[str, Type[AppTemplate]] = {}
        self.hide_st_stuff = hide_st_stuff
        self.home_app = None
        self.in_development = in_development
        self.home_sidebar = True
        self.group_parent = group_parent
        self.name = name
        self.hidden_apps = []
        self.debug = debug
        if self.debug:
            self.hide_st_stuff = False
        
        if not self.group_parent:
            self.setup_app()

        #self.params = loadconfig()

        self.__dict__.update(kwargs)

    def add_page(self, title: str, page_class: Type[AppTemplate], is_home=False, is_hidden = False, show_sidebar=True) -> None:

        if is_home:
            self.home_app = title
        
        if is_hidden:
            self.hiddenpages[title] = page_class(title=title,group=self.name, debug=self.debug, home_app=self.home_app, parent=self, in_development=self.in_development)
        else:
            self.pages[title] = page_class(title=title,group=self.name, debug=self.debug, home_app=self.home_app, show_sidebar=show_sidebar, parent=self, in_development=self.in_development)

    def setup_app(self) -> None:

        if self.hide_st_stuff:
            st.markdown(HIDE_ST_STYLE, unsafe_allow_html=True)


    # Utility function to get the page from URL query parameters
    def get_page_from_url(self) -> str:
        return st.query_params.get("page", self.home_app)

    # Function to navigate to a new page
    def navigate_to_page(self, page: str) -> None:
        
        st.query_params.page = page
        st.session_state.current_page = page
        st.rerun(scope="app")

    def welcome(self):
        if st.session_state.get('username',None):
            username = st.session_state.get('username',None)
            displayname = st.session_state.get('displayname',None)

            st.sidebar.write("Welcome {}".format(displayname))

            # if st.sidebar.link_button("logout","/?page=&monitoring=tools"):
            #     st.session_state.access_level = 0
            #     st.session_state.username = None


    def render_sidebar(self, url_page):

        selected_page = url_page
        current_page_class = self.pages[url_page]

        if current_page_class.show_sidebar:
            self.welcome()
            st.sidebar.image("./static/Ngenux.jpeg")
            # st.sidebar.header("{} Monitoring Application :stethoscope:".format(self.name.upper()),divider="rainbow")
            # st.sidebar.subheader('Analysis Selector')  

            # selected_page = st.sidebar.selectbox(
            #     "Select the analysis you want to view",
            #     options=list(self.pages.keys()),
            #     index=list(self.pages.keys()).index(url_page)
            # )

        return selected_page


    def run(self) -> None:

        url_page = self.get_page_from_url()

        # Initialize session state
        if 'current_page' not in st.session_state:
            st.session_state.current_page = url_page     


        if url_page in self.hiddenpages.keys():
            current_page_class = self.hiddenpages[url_page]
            current_page_class.load()
            
        else:
            selected_page = self.render_sidebar(url_page)
            current_page_class = self.pages[selected_page]
            

            # Handle page navigation
            if selected_page != url_page:
                self.navigate_to_page(selected_page)

            # Render the current page
            current_page_class.load()


class GroupMultiPageApp(ABC):
    def __init__(self, name,home_app=None, hide_st_stuff = True, debug=False, in_development=False, **kwargs):
        self.groups: Dict[str, Type[MultiPageApp]] = {}
        self.hide_st_stuff = hide_st_stuff
        self.home_app = home_app
        self.name = name
        self.in_development = in_development
        self.debug = debug

        if self.debug:
            self.hide_st_stuff = False

        self.setup_app()

        self.__dict__.update(kwargs)


    def add_group(self, title: str, group_app: Type[MultiPageApp]) -> None:        

        self.groups[title] = group_app


    def setup_app(self) -> None:

        if self.hide_st_stuff:
            st.markdown(HIDE_ST_STYLE, unsafe_allow_html=True)


    def run(self):

        selected_monitoring_app = st.query_params.get("app", "")
        selected_page = st.query_params.get("page", "")

        if selected_page == 'hadmin':
            self.groups['tools'].run()
        else:
            if selected_monitoring_app == "":
                self.home_app.run()
            else:
                if selected_monitoring_app in self.groups.keys():
                    self.groups[selected_monitoring_app].run()
                else:
                    self.home_app.run()