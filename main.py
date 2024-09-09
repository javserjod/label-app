import streamlit as st
from streamlit_option_menu import option_menu
import home, upload_data, edit_data, data_information, graphic_labelling


st.set_page_config(page_title = "Label App",        # name shown in the browser tab
                   page_icon="",                    # icon shown in the browser tab, before the name
                   layout="centered")               # set the page layout to wide

# Create a class to manage the app
class LabelApp:
    def __init__(self):
        self.apps = []
    
    def add_app(self, title, function):
        self.apps.append({
            "title": title,
            "function": function
        })

    def run():
        with st.sidebar:
            app = option_menu(
                menu_title = "Navigation Menu",
                menu_icon = "",             # bootstrap icons
                options = ["Home", "Upload Data", "Edit Data", "Graphic Labelling", "Data Information"],
                icons = ["house", "upload", "pencil", "tag", "info-circle"],    # bootstrap icons
                default_index = 0,      # start index when page is loaded
            )

        if app == "Home":
            home.app()
                
        if app == "Upload Data":
            upload_data.app()
            
        if app == "Edit Data":
            edit_data.app()
                
        if app == "Graphic Labelling":
            graphic_labelling.app()

        if app == "Data Information":
            data_information.app()


    run()