import streamlit as st

'''file to store the reset functions for each session state variable in the graphic labelling page'''

def reset_all_session_state() -> None:
    # resets all session state variables in the graphic labelling page to default values
    reset_line_chart_session_state()  # reset the line chart session state variables
    reset_scatter_plot_session_state()  # reset the scatter plot session state variables
    reset_bar_chart_session_state()  # reset the bar chart session state variables

    reset_common_session_state()
    reset_labelling_session_state()  # reset the labelling section session state variables

    st.cache_data.clear()         # clear all the cache data 



def reset_line_chart_session_state() -> None:
    # reset line chart session state variables to default values
    st.session_state.line_chart_toggle_time_series = True
    st.session_state.line_chart_toggle_time_axis = True
    st.session_state.freq_number_input = 1.00
    st.session_state.line_chart_time_column = []
    st.session_state.line_chart_column_against = []
    st.session_state.line_chart_painting_time_series = []   # could be a labelling session state
    st.session_state.line_chart_painting_against = []     
    st.session_state.color_picker = "#6B5858"    # default color
    
    
def reset_scatter_plot_session_state() -> None:
    # reset scatter plot session state variables to default values
    st.session_state.scatter_plot_painting = []  
    

def reset_bar_chart_session_state() -> None:
    # reset bar chart session state variables to default values
    st.session_state.barmode_index = 0   
    st.session_state.bar_chart_painting = []
    st.session_state.translated_indexes = []       # default value



def reset_common_session_state() -> None:
    # reset common session state variables to default values
    st.session_state.chart_title = ""  
    st.session_state.x_axis_variable_index = 0
    st.session_state.y_axis_variable_index = 0
    st.session_state.multiselect_y_axis_variable = []
    st.session_state.chart_color_variable_index = 0  
    
    
def reset_labelling_session_state() -> None:
    # reset labelling section session state variables to default values
    st.session_state.label_classes = []
    st.session_state.currently_selected_class = []         
    st.session_state.selected_data = None
    st.session_state.label_column = [""] * st.session_state.dataset.shape[0]    # adjust number of rows
    st.session_state.label_column_name = "label_column" 
    st.session_state.labelled_dataset = None
    st.session_state.chart_toggle_color = True
    
    
    