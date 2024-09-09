import streamlit as st
import pandas as pd

def app():
    
    #------------------------ SESSION STATE -------------------------#
    # No new session state keys, just modifying the values of dataset (created in upload_data.py)
    
    
    #-------------------------- FUNCTIONS ---------------------------#
    def get_current_headers() -> list:
        # returns the current headers of the dataset being edited
        return st.session_state.dataset.columns.tolist()
    

    #---------------------------- PAGE ------------------------------#
    if st.session_state.dataset is not None:   # if any data was uploaded
        st.header("Edit Data")
        st.subheader(f"File name: {st.session_state.file_name}")
        st.session_state.dataset = st.data_editor(st.session_state.dataset,
                                                    use_container_width = True,
                                                    num_rows = "dynamic")
        
        with st.expander("Modify headers"):
            with st.form("header_form"):
                
                st.text("Write the new headers' names for the dataset:")  
                
                written_headers = [None] * len(st.session_state.dataset.columns)   # variabel to store text_input values
                for i in range(0, len(st.session_state.dataset.columns)):
                    written_headers[i] = st.text_input(f"Header {i}", value = st.session_state.dataset.columns[i])
                    
                new_headers = st.toggle("Move down current headers and insert the new ones?",
                                        help = "Selecting this option will insert the current headers as the first row, and create new headers with the values given. Not selecting this option will just rename the current headers with the indicated values.")  
                
                submitted = st.form_submit_button("Submit")
                if submitted:
                    if new_headers:    # move down current headers and insert the new ones
                        current_headers = get_current_headers()   # get the current headers
                        st.session_state.dataset = st.session_state.dataset.set_axis(written_headers, axis="columns")    # change the headers to the default ones
                        st.session_state.dataset = pd.concat([pd.DataFrame([current_headers], columns=written_headers), 
                                                            st.session_state.dataset], ignore_index=True)     # join previous headers as first row, resulting in one dataset with default headers
                        st.session_state.dataset.reset_index(drop=True, inplace=True)   # reset the index of the dataset, so it starts from 0 and goes up consecutive numbers
                    
                    else:   # just rename the headers
                        st.session_state.dataset.columns = written_headers

                    st.rerun()   # rerun the app to update the table
        
    else:
        st.write("Please, upload a file first...")