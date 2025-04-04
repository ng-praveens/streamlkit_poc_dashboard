from abc import ABC, abstractmethod
import streamlit as st
from apps.common import Loader, Loaders


class AppTemplate(ABC):
    """
    This is a template class that streamlit applications can inherit from that automatically structures them for use in a Multi-page application.

    A number of convenience methods are also included within the template.
    
    """

    def __init__(self, title=None, group=None, params=None, home_app="",debug = False,in_development=False, show_sidebar = True, parent=None, **kwargs):
        self.title = title
        self.group = group
        self.in_development = in_development
        self.show_sidebar = show_sidebar
        self.home_app = home_app

        if params:
            self.app_params = params['apps'].get(title,{})
            self.general_params = params.get('general',{})
        else:
            self.app_params = {}
            self.general_params = {}

        #details from parent
        self.parent = parent
        
        self.debug = debug
        self.__dict__.update(kwargs)


    def load(self):
        try:
            #redirect = False
            st.query_params.page = self.title

            #with Loader("Now loading {}".format(self.title), loader_name=Loaders.standard_loaders,index=[3,0,5]):               
            with st.empty().container():
                _left, _centre, _right = st.columns([2,10,2])
                with _left:
                    if self.title!=self.home_app:
                        # if st.button("{} Home ".format(self.group.title())):
                        #     self.parent.navigate_to_page(self.home_app)
                        st.html("""<a href="/?page={}&monitoring={}" target="_parent">{} Home</a>""".format(self.home_app,self.group,self.group.upper()))
                
                with _right:
                    # if st.button("Monitors Home"):
                    #     st.query_params.clear()
                    #     del st.session_state['current_page']
                    #     st.rerun()
                    
                    st.html("""<a href="/" target="_parent">Monitors Home</a>""")

                if self.debug:
                    st.subheader("Session state inspector")
                    #st.write(self.global_state.__dict__)
                    st.write(dict(st.session_state))

                self.run()


      
        except Exception as e:
            if self.debug:
                st.write(e)
            else:
                st.toast("An error has occured, please try again.")


    @abstractmethod
    def run(self):
        raise NotImplementedError("Each page must implement a `run` method.")