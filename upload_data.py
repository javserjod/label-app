import streamlit as st
import pandas as pd
import os

# import resetting for every session state variable in plot in graphic labelling
from reset_functions import reset_all_session_state

def app():
    
    #-------------------------- FUNCTIONS ---------------------------#
    def load_data() -> None:
    # read file and store it in session state, also file name. and reset all charts variables from session state to default value
        #st.session_state.original_dataset = pd.read_csv(uploaded_file, delimiter='[;,]', engine='python')  # read the file
        st.session_state.original_dataset = pd.read_csv(uploaded_file, sep=None, engine='python')  # read the file, DETECT/INFER THE DELIMITER
        convert_boolean_columns()   # convert actually boolean columns to boolean type instead of int64 (due to bad inference when reading the file)
        convert_datetime_columns()  # convert actually datetime columns to datetime type instead of object (due to bad inference when reading the file)
        
        st.session_state.dataset = st.session_state.original_dataset.copy()  # copy the original dataset
        st.session_state.file_name =  uploaded_file.name
        
        # save the name of the file to be downloaded, removing its extension, whatever it is
        dot_index = st.session_state.file_name.rfind(".")    # find the index of last dot in the file name
        st.session_state.download_file_name = st.session_state.file_name[:dot_index] + "_modified"  # default name of the file to be downloaded (used in Data Edit)

        #reset graph type selection in graphic labelling
        st.session_state.graph_selectbox_index = 0
        # reset all charts variables from session state to default value
        reset_all_session_state()    # reset all charts and labelling variables from session state to default value
    
        
    def convert_boolean_columns() -> None:
        # search for int64 columns with only 0s and 1s try to convert them to boolean (they are probably boolean columns). Also convert yes/no or true/false to boolean 1/0
        for column_name in st.session_state.original_dataset.select_dtypes(include=['int64', 'object']).columns:
            unique_values = st.session_state.original_dataset[column_name].unique()
            
            # if the column has only 0s and 1s (or only one of them), convert it to boolean
            if set(unique_values) <= {0, 1} and len(unique_values) >= 1:
                st.session_state.original_dataset[column_name] = st.session_state.original_dataset[column_name].astype(bool)
            
            # if the column has only "yes"/"no" or "true"/"false", convert it to boolean
            try:
                if set([val.lower() for val in unique_values]) <= {"yes", "no"} and len(unique_values) >= 1:
                    st.session_state.original_dataset[column_name] = st.session_state.original_dataset[column_name].astype(bool)
                
                if set([val.lower() for val in unique_values]) <= {"true", "false"} and len(unique_values) >= 1:
                    st.session_state.original_dataset[column_name] = st.session_state.original_dataset[column_name].astype(bool)
            except:
                pass   # if it is not possible to convert to lower case, just pass
            
    def convert_datetime_columns() -> None:
        # search for object columns that can store datetime values, and convert them
        for column_name in st.session_state.original_dataset.select_dtypes(include=['object']).columns:
            try:
                st.session_state.original_dataset[column_name] = pd.to_datetime(st.session_state.original_dataset[column_name])
            except:
                pass  # if it is not possible to convert to datetime, just pass
    
        
    #---------------------------- PAGE ------------------------------#
    st.header("Upload Data")
    
    uploaded_file = st.file_uploader(label=":file_folder: Upload a file", 
                        type=['csv'])
    
    if uploaded_file is not None:   # when a file is uploaded
        try:
            load_data()
            st.success("Data loaded successfully!", icon="✅")
        except Exception as e:
            st.error("Error while uploading the file. Please try again..."+str(e), icon="🚨")
    
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
        
        st.markdown("######")   # add space between the metrics and the description
        with st.expander("Show dataset description"):
            st.dataframe(st.session_state.original_dataset.describe(include="all").T, use_container_width = True)
            
    else:
        st.info("Please, upload a file first on the above component", icon=":material/help_center:")    # if no file uploaded, show info message
        