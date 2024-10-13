import streamlit as st
from streamlit_option_menu import option_menu
import home, upload_data, edit_data, data_information, graphic_labelling

#if __name__ == "__main__":   # does not work with streamlit community cloud deployment
    
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


# edit data session state variables ...............................................

if "filtered_dataset" not in st.session_state:      # to store the filtered dataset temporary
    st.session_state.filtered_dataset = None
    
if "download_file_name" not in st.session_state:    # to store the name of the file to be downloaded
    st.session_state.download_file_name = None      # assign default value when uploading dataset


# line chart session state variables ...............................................
    
if "line_chart_toggle_time_series" not in st.session_state:
    st.session_state.line_chart_toggle_time_series = True    # default value (insert in number input)
    
if "line_chart_toggle_time_axis" not in st.session_state:
    st.session_state.line_chart_toggle_time_axis = True    # default value (insert in number input)
    
if "freq_number_input" not in st.session_state:
    st.session_state.freq_number_input = 1.00       # default value
    
if "line_chart_time_column" not in st.session_state:
    st.session_state.line_chart_time_column = []       # default value (only one string allowed)
    
if "line_chart_time_axis" not in st.session_state:
    st.session_state.line_chart_time_axis = []       # default value
    
if "line_chart_column_against" not in st.session_state:
    st.session_state.line_chart_column_against = []    # default value (only one string allowed)

if "line_chart_painting_time_series" not in st.session_state:
    st.session_state.line_chart_painting_time_series = []       # default value
    
if "line_chart_painting_against" not in st.session_state:
    st.session_state.line_chart_painting_against = []       # default value

if "color_picker" not in st.session_state:
    st.session_state.color_picker = "#6B5858"       # default value



# scatter plot session state variables ...............................................
if "toggle_color_label_variable" not in st.session_state:
    st.session_state.toggle_color_label_variable = True    # default toggle active
    
if "list_color_classes" not in st.session_state:
    # to storre the equivalent color for each class
    st.session_state.list_color_classes = []       # default value

if "scatter_plot_painting" not in st.session_state:
    st.session_state.scatter_plot_painting = []       # default value



# bar chart session state variables ...............................................
if "barmode_index" not in st.session_state:
    st.session_state.barmode_index = 0       # default value

if "bar_chart_painting" not in st.session_state:
    st.session_state.bar_chart_painting = []       # default value

if "translated_indexes" not in st.session_state:
    st.session_state.translated_indexes = []       # default value


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
    
if "chart_toggle_color" not in st.session_state:
    st.session_state.chart_toggle_color = True    # default value (insert in number input)
    

# common for more than 1 chart session state variables ...............................................

if "chart_title" not in st.session_state:
    st.session_state.chart_title = ""       # default value
    
if "x_axis_variable_index" not in st.session_state:
    st.session_state.x_axis_variable_index = None      # default value None, so no graphic is plotted at first
    
if "y_axis_variable_index" not in st.session_state:
    st.session_state.y_axis_variable_index = None      # default value None, so no graphic is plotted at first
    
if "multiselect_y_axis_variable" not in st.session_state:
    st.session_state.multiselect_y_axis_variable = []       # default value
    
if "chart_color_variable_index" not in st.session_state:
    # to store the index of the chosen color variable in selectbox
    st.session_state.chart_color_variable_index = None        # default value None, so no graphic is plotted at first



# app theme control ...............................................

if 'current_app_theme' not in st.session_state:
    st.session_state.current_app_theme = 'dark'    # start dark mode


def theme_button_icon() -> str:
    # returns right theme button icon according to the session state variable 
    return ":material/dark_mode:" if st.session_state.current_app_theme == 'dark' else ":material/light_mode:"

    
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
            if st.button(label=theme_button_icon(), help="Switch between light and dark mode. Page reruns"):
                if st.session_state.current_app_theme=='light':    #then change to dark mode
                    st._config.set_option(f'theme.base', "dark")   # inherit from predefined dark theme
                    st._config.set_option(f'theme.backgroundColor', "#0E1117")
                    st._config.set_option(f'theme.primaryColor', "#FF4B4B") 
                    st._config.set_option(f'theme.secondaryBackgroundColor', "#262730")
                    st._config.set_option(f'theme.textColor', "#FAFAFA")
                    st._config.set_option(f'theme.font', "sans serif")
                    st.session_state.current_app_theme = 'dark'   # change the theme to dark
                else:   # change to light mode
                    st._config.set_option(f'theme.base', "light")   # inherit from predefined light theme
                    #st._config.set_option(f'theme.primaryColor', "#FF4B4B")
                    #st._config.set_option(f'theme.backgroundColor', "#FFFFFF")
                    #st._config.set_option(f'theme.secondaryBackgroundColor', "#F0F2F6")
                    #st._config.set_option(f'theme.textColor' , "#31333F")
                    # a bit darker than light theme
                    st._config.set_option('theme.primaryColor', "#CC3B3B")
                    st._config.set_option('theme.backgroundColor', "#E0E0E0") 
                    st._config.set_option('theme.secondaryBackgroundColor', "#D0D3DB")  
                    st._config.set_option('theme.textColor', "#1F2028") 
                    
                    st._config.set_option(f'theme.font', "sans serif")
                    st.session_state.current_app_theme = 'light'   # change the var theme to light 
                st.rerun()
            
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