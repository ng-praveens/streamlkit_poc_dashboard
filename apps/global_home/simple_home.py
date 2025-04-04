import streamlit as st
from core import navigation_card
import base64
from core.misc_utils import loadconfig


@st.cache_data(ttl="1d")
def load_static_resources():

    resources = {}

    with open("./static/edtech.png", "rb") as image_file:
        resources["edtech_base64"] = base64.b64encode(image_file.read()).decode("utf-8")

    with open("./static/doc_parsing.png", "rb") as image_file:
        resources["parser_base64"] = base64.b64encode(image_file.read()).decode("utf-8")

    # with open("./static/doc_verification.png", "rb") as image_file:
    #     resources["verify_base64"] = base64.b64encode(image_file.read()).decode("utf-8")

    with open("./static/chatbot.jpg", "rb") as image_file:
        resources["chat_base64"] = base64.b64encode(image_file.read()).decode("utf-8")

    with open("./static/email.png", "rb") as image_file:
        resources["email_base64"] = base64.b64encode(image_file.read()).decode("utf-8")

    with open("./static/doc_verification.png", "rb") as image_file:
        resources["sidf_base64"] = base64.b64encode(image_file.read()).decode("utf-8")

    return resources


class SimpleGlobalHomePage:

    def __init__(self, debug=False, in_development=False, **kwargs):

        self.title = "Generative AI Applications"
        self.subtitle = "brought to you by the Data Science and Analytics Team."

        self.debug = debug
        self.in_development = in_development
        self.__dict__.update(kwargs)

    def run(self):

        resources = load_static_resources()

        _left, _centre, _right = st.columns([2, 7, 2])

        with _left:
            st.image("./static/icon.png", width=100)

        with _centre:
            st.markdown(
                "<h1 style='text-align:center;padding: 0px 0px;color:black;font-size:300%;'>{title}</h1><h4 style='text-align:center;color:grey;font-size:100%;'><i>{subtitle}</i></h4>".format(
                    title=self.title, subtitle=self.subtitle
                ),
                unsafe_allow_html=True,
            )

        st.divider()
        with st.container():
            with st.spinner("Loading monitoring apps.................."):
                c1, c2 = st.columns(2)
                with c1:
                    navigation_card(
                        "Chatbot",
                        "AI-powered application designed to simulate conversation with users, either via text or voice. It can assist with customer service, provide information in meaningful dialogues, leveraging Natural Language Processing (NLP).",
                        resources["chat_base64"],
                        "/?app=chat&page=Chat+Home+Page",
                    )
                    navigation_card(
                        "Edtech Application",
                        "Summarizes educational videos, generates question-and-answer pairs, and creates detailed notes to enhance learning and comprehension.",
                        resources["edtech_base64"],
                        "/?app=edtech&page=Edtech+Home+Page",
                    )
                    navigation_card(
                        "Document Parsing",
                        "Processes the document and converts it into machine-readable formats such as JSON and Markdown",
                        resources["parser_base64"],
                        "/?app=docp&page=Doc+Parser+Home+Page",
                    )
                with c2:
                    navigation_card(
                        "Personalized Emails",
                        "Crafts personalized emails tailored to individual preferences and requirements, ensuring effective communication and engagement.",
                        resources["email_base64"],
                        "/?app=email&page=Personalized+Email+Home+Page",
                    )
                    # navigation_card(
                    #     "Document Verification",
                    #     "Performs document verification by analyzing and validating content to ensure accuracy, authenticity, and compliance with specified requirements.",
                    #     resources["verify_base64"],
                    #     "/?app=docv&page=Doc+Verification+Home+Page",
                    # )
                    navigation_card(
                        "Document processing",
                        "Performs document verification by analyzing and validating content to ensure accuracy, authenticity, and compliance with specified requirements.",
                        resources["sidf_base64"],
                        "/?app=sidf&page=Document+Processing+App",
                    )
