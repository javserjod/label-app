import streamlit as st
from streamlit_option_menu import option_menu
import home, upload_data, edit_data, data_information, graphic_labelling


st.set_page_config(page_title = "Label App",        # name shown in the browser tab
                   page_icon="",                    # icon shown in the browser tab, before the name
                   layout="wide")                   # set the page layout to wide


#------------------------ SESSION STATE -------------------------#
# create in first run session state values

if "original_dataset" not in st.session_state:      # to store the original dataset
    st.session_state.original_dataset = None
        
if "dataset" not in st.session_state:               # to store copy of dataset that will be modified
    st.session_state.dataset = None
        
if "file_name" not in st.session_state:             # to store the uploaded file name
    st.session_state.file_name = None

if "graph_selectbox_index" not in st.session_state:       # to store the index of the chosen graph type in selectbox
    st.session_state.graph_selectbox_index = 0      # default value

# line chart session state variables ...............................................
if "line_chart_y_axis" not in st.session_state:
    st.session_state.line_chart_y_axis = []       # default value
    
if "line_chart_toggle_time_series" not in st.session_state:
    st.session_state.line_chart_toggle_time_series = True    # default value (insert in number input)
    
if "line_chart_toggle_time_axis" not in st.session_state:
    st.session_state.line_chart_toggle_time_axis = True    # default value (insert in number input)
    
if "freq_number_input" not in st.session_state:
    st.session_state.freq_number_input = 1.00       # default value
    
if "line_chart_time_column" not in st.session_state:
    st.session_state.line_chart_time_column = []       # default value (only one string allowed)
    
if "line_chart_column_against" not in st.session_state:
    st.session_state.line_chart_column_against = []    # default value (only one string allowed)

if "line_chart_title" not in st.session_state:
    st.session_state.line_chart_title = "Line Chart"       # default value

# scatter plot session state variables ...............................................
if "scatter_x_axis_index" not in st.session_state:
    st.session_state.scatter_x_axis_index = 0       # default value
       
if "scatter_y_axis_index" not in st.session_state:
    st.session_state.scatter_y_axis_index = 0       # default value
      
if "scatter_color_index" not in st.session_state:
    st.session_state.scatter_color_index = 0        # default value

# 
if "selected_data" not in st.session_state:         # to store the selected data from graph
    st.session_state.selected_data = None
    

#----------------------- APP CONTROL ---------------------------#
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


    
def reset_line_chart_session_state() -> None:
        # reset line chart session state variables to default values
        st.session_state.line_chart_y_axis = []
        st.session_state.line_chart_toggle_time_series = True
        st.session_state.line_chart_toggle_time_axis = True
        st.session_state.freq_number_input = 1.00
        st.session_state.line_chart_time_column = []
        st.session_state.line_chart_column_against = []
        st.session_state.line_chart_title = "Line Chart"