import streamlit as st
from PIL import Image

from core import MultiPageApp, GroupMultiPageApp
from apps.global_home.simple_home import SimpleGlobalHomePage
from apps.edtech_home.home import EdtechHomePage

# from apps.docv_home.home import DocVerificationHomePage
from apps.docp_home.home import DocParserHomePage
from apps.chat_home.home import ChatHomePage
from apps.email_home.home import PersonalizedEmailHomePage

from apps.sidf_home.home import DocumentProcessingApp

if __name__ == "__main__":
    RUN_DEBUG = False
    IN_DEVELOPMENT = False
    try:
        img = Image.open("./static/favicon.ico")
        st.set_page_config(
            page_title="Model Monitoring Application", page_icon=img, layout="wide"
        )
    except BaseException as e:
        st.rerun()

    group_app = GroupMultiPageApp(
        name="Group model monitoring apps",
        home_app=SimpleGlobalHomePage(debug=RUN_DEBUG, in_development=IN_DEVELOPMENT),
        debug=RUN_DEBUG,
        in_development=IN_DEVELOPMENT,
    )

    edtech_app = MultiPageApp(
        name="edtech",
        group_parent=group_app,
        debug=RUN_DEBUG,
        in_development=IN_DEVELOPMENT,
    )
    group_app.add_group("edtech", edtech_app)
    edtech_app.add_page("Edtech Home Page", EdtechHomePage, is_home=True)

    # doc_verification_app = MultiPageApp(
    #     name="docv",
    #     group_parent=group_app,
    #     debug=RUN_DEBUG,
    #     in_development=IN_DEVELOPMENT,
    # )
    # group_app.add_group("docv", doc_verification_app)
    # doc_verification_app.add_page(
    #     "Doc Verification Home Page", DocumentProcessingApp, is_home=True
    # )

    doc_parser_app = MultiPageApp(
        name="docp",
        group_parent=group_app,
        debug=RUN_DEBUG,
        in_development=IN_DEVELOPMENT,
    )
    group_app.add_group("docp", doc_parser_app)
    doc_parser_app.add_page("Doc Parser Home Page", DocParserHomePage, is_home=True)

    chat_app = MultiPageApp(
        name="chat",
        group_parent=group_app,
        debug=RUN_DEBUG,
        in_development=IN_DEVELOPMENT,
    )
    group_app.add_group("chat", chat_app)
    chat_app.add_page("Chat Home Page", ChatHomePage, is_home=True)

    email_app = MultiPageApp(
        name="email",
        group_parent=group_app,
        debug=RUN_DEBUG,
        in_development=IN_DEVELOPMENT,
    )
    group_app.add_group("email", email_app)
    email_app.add_page(
        "Personalized Email Home Page", PersonalizedEmailHomePage, is_home=True
    )

    sidf_app = MultiPageApp(
        name="sidf",
        group_parent=group_app,
        debug=RUN_DEBUG,
        in_development=IN_DEVELOPMENT,
    )
    group_app.add_group("sidf", sidf_app)

    sidf_app.add_page("Document Processing App", DocumentProcessingApp, is_home=True)

    # Run the app
    group_app.run()
