import streamlit as st
import pandas as pd

def app():
    
    #------------------------ SESSION STATE -------------------------#
    # create in first run session state values
    if "original_dataset" not in st.session_state:  # to store the original dataset
        st.session_state.original_dataset = None
        
    if "dataset" not in st.session_state:   # to store the read dataset
        st.session_state.dataset = None
        
    if "file_name" not in st.session_state:  # to store the uploaded file name
        st.session_state.file_name = None


    #-------------------------- FUNCTIONS ---------------------------#
    def load_data() -> None:
        # read file and store it in session state, also file name
        st.session_state.original_dataset = pd.read_csv(uploaded_file)
        st.session_state.dataset = st.session_state.original_dataset.copy()  # copy the original dataset
        st.session_state.file_name =  uploaded_file.name
        st.write("Data loaded successfully!")
    
    #---------------------------- PAGE ------------------------------#
    st.header("Upload Data")
    
    uploaded_file = st.file_uploader(label=":file_folder: Upload a file", 
                        type=['csv'])
    
    
    if uploaded_file is not None:   # when a file is uploaded
        load_data()
    
    
    if st.session_state.original_dataset is not None:   # if any data was uploaded
        st.divider()
        st.header("Preview Uploaded Data")
        st.subheader(f"File name: {st.session_state.file_name}")
        st.dataframe(st.session_state.original_dataset, use_container_width = True)
        
    else:
        st.write("No file uploaded yet...")
        