import streamlit as st
import pandas as pd
import os

# import resetting for every session state variable in plot in graphic labelling
from reset_functions import reset_all_session_state

def app():
    
    #-------------------------- FUNCTIONS ---------------------------#
    def load_data() -> None:
    # read file and store it in session state, also file name. and reset all charts variables from session state to default value
        st.session_state.original_dataset = pd.read_csv(uploaded_file)
        st.session_state.dataset = st.session_state.original_dataset.copy()  # copy the original dataset
        st.session_state.file_name =  uploaded_file.name
    
        #reset graph type selection in graphic labelling
        st.session_state.graph_selectbox_index = 0
        # reset all charts variables from session state to default value
        reset_all_session_state()    # reset all charts and labelling variables from session state to default value
        
        
    #---------------------------- PAGE ------------------------------#
    st.header("Upload Data")
    
    uploaded_file = st.file_uploader(label=":file_folder: Upload a file", 
                        type=['csv'])
    
    if uploaded_file is not None:   # when a file is uploaded
        try:
            load_data()
            st.success("Data loaded successfully!", icon="✅")
        except:
            st.error("Error while uploading the file. Please try again...", icon="🚨")
    
    if st.session_state.dataset is not None:   # if any data was uploaded
        st.divider()
        st.header("Preview Uploaded Data")
        st.subheader(f"File name: {st.session_state.file_name}")
        st.dataframe(st.session_state.original_dataset, use_container_width = True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Number of rows", value=st.session_state.original_dataset.shape[0])
        with col2:
            st.metric("Number of columns", value=st.session_state.original_dataset.shape[1])
        with col3:
            memory_usage=st.session_state.original_dataset.memory_usage(deep=True).sum()   # sum of memory usage of each column = total (BYTES)
            size_in_kb = f"{memory_usage/(1024):.2f}"
            size_in_mb = f"{memory_usage/(1024**2):.2f}"
            st.metric("Size of dataset in memory", value=size_in_mb+" MB" if float(size_in_mb) > 1 else size_in_kb+" kB", 
                      help="Size in memory after loading the file, which may differ from the actual file size due to Pandas conversion")
        
    else:
        st.warning("No file uploaded yet...")
        