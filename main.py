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

if "line_chart_painting_time_series" not in st.session_state:
    st.session_state.line_chart_painting_time_series = []       # default value
    
if "line_chart_painting_against" not in st.session_state:
    st.session_state.line_chart_painting_against = []       # default value

if "color_picker" not in st.session_state:
    st.session_state.color_picker = "#E6A9A9"       # default value pink

if "line_chart_toggle_color" not in st.session_state:
    st.session_state.line_chart_toggle_color = True    # default value (insert in number input)



# scatter plot session state variables ...............................................
if "scatter_x_axis_index" not in st.session_state:
    st.session_state.scatter_x_axis_index = 0       # default value
       
if "scatter_y_axis_index" not in st.session_state:
    st.session_state.scatter_y_axis_index = 0       # default value
      
if "scatter_color_index" not in st.session_state:
    st.session_state.scatter_color_index = 0        # default value


# labelling section session state variables ...............................................
    
if "label_classes" not in st.session_state:         # to store the classes of the label
    st.session_state.label_classes = []             # default value
    
if "currently_selected_class" not in st.session_state:    # to store the currently selected class
    st.session_state.currently_selected_class = []          # default value

if "selected_data" not in st.session_state:         # to store the selected data from any graph
    st.session_state.selected_data = None

if "label_column" not in st.session_state:          # to store the column thats contains the label
    st.session_state.label_column = None            # change default value after uploading or editing dataset
    
if "label_column_name" not in st.session_state:     # to store the name of the label column
    st.session_state.label_column_name = "label_column"         # default value
        
if "labelled_dataset" not in st.session_state:      # to store the labelled dataset
    st.session_state.labelled_dataset = None

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