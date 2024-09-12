import streamlit as st
import pandas as pd
# import resetting for every session state variable in plot in graphic labelling
from main import reset_line_chart_session_state

def app():
    
    #-------------------------- FUNCTIONS ---------------------------#
    def load_data() -> None:
        
        # read file and store it in session state, also file name
        st.session_state.original_dataset = pd.read_csv(uploaded_file)
        st.session_state.dataset = st.session_state.original_dataset.copy()  # copy the original dataset
        st.session_state.file_name =  uploaded_file.name
        st.write("Data loaded successfully!")
    
        #reset graph type selection in graphic labelling
        st.session_state.graph_selectbox_index = 0
        # reset all charts variables from session state to default value
        reset_line_chart_session_state()    # reset the line chart session state variables

        
    #---------------------------- PAGE ------------------------------#
    st.header("Upload Data")
    
    uploaded_file = st.file_uploader(label=":file_folder: Upload a file", 
                        type=['csv'])
    
    if uploaded_file is not None:   # when a file is uploaded
        load_data()
    
    if st.session_state.dataset is not None:   # if any data was uploaded
        st.divider()
        st.header("Preview Uploaded Data")
        st.subheader(f"File name: {st.session_state.file_name}")
        st.dataframe(st.session_state.original_dataset, use_container_width = True)
        
    else:
        st.write("No file uploaded yet...")
        