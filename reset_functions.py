import streamlit as st

'''file to store the reset functions for each session state variable in the graphic labelling page'''

def reset_all_session_state() -> None:
    reset_line_chart_session_state()  # reset the line chart session state variables
    reset_scatter_plot_session_state()  # reset the scatter plot session state variables

    reset_labelling_session_state()  # reset the labelling section session state variables




def reset_line_chart_session_state() -> None:
    # reset line chart session state variables to default values
    st.session_state.line_chart_y_axis = []
    st.session_state.line_chart_toggle_time_series = True
    st.session_state.line_chart_toggle_time_axis = True
    st.session_state.freq_number_input = 1.00
    st.session_state.line_chart_time_column = []
    st.session_state.line_chart_column_against = []
    st.session_state.line_chart_title = "Line Chart"
    
    
def reset_scatter_plot_session_state() -> None:
    # reset scatter plot session state variables to default values
    st.session_state.scatter_x_axis_index = 0
    st.session_state.scatter_y_axis_index = 0
    st.session_state.scatter_color_index = 0
    
    
def reset_labelling_session_state() -> None:
    # reset labelling section session state variables to default values
    st.session_state.label_classes = []
    st.session_state.currently_selected_class = []         
    st.session_state.selected_data = None
    st.session_state.label_column = [""] * st.session_state.dataset.shape[0]    # adjust number of rows
    st.session_state.label_column_name = "label_column" 
    st.session_state.labelled_dataset = None