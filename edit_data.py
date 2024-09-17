import streamlit as st
import pandas as pd

# import resetting for every session state variable in plot in graphic labelling
from reset_functions import reset_all_session_state

def app():
    
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
                
                written_headers = [None] * len(st.session_state.dataset.columns)   # variable to store text_input values
                for i in range(0, len(st.session_state.dataset.columns)):
                    written_headers[i] = st.text_input(f"Header {i}", value = st.session_state.dataset.columns[i])    # stored as strings
                    
                new_headers = st.toggle("Move down current headers and insert the new ones?",
                                        help = "Selecting this option will insert the current headers as the first row, and create new headers with the values given. Not selecting this option will just rename the current headers with the indicated values.")  
                
                submitted = st.form_submit_button("Submit")
                if submitted:      # execute headers modification
                    
                    if new_headers:    # move down current headers and insert the new ones  
                        # do type conversion since existing reference row
                        current_headers = get_current_headers()                 # get the current headers

                        if len(st.session_state.dataset.values) > 0:                        # conversion only if there's at least one existing row (needed to have a reference for the types)
                            for i in range(len(st.session_state.dataset.columns)):          # iterate over the previous headers to force type conversion
                                if type(current_headers[i]) != str:                         #conversion only if not string
                                    current_headers[i] = type(st.session_state.dataset.values[0][i])(current_headers[i])   # force the type conversion if not string
                        
                        st.session_state.dataset = st.session_state.dataset.set_axis(written_headers, axis="columns")    # change the headers to the written ones
                        st.session_state.dataset = pd.concat([pd.DataFrame([current_headers], columns=written_headers), 
                                                                st.session_state.dataset], ignore_index=True)     # join previous headers as first row, resulting in one dataset with default headers
                        st.session_state.dataset.reset_index(drop=True, inplace=True)   # reset the index of the dataset, so it starts from 0 and goes up consecutive numbers
                    
                    else:   # just rename the headers
                        st.session_state.dataset.columns = written_headers

                    reset_all_session_state()   # reset all charts and labelling variables from session state to default value
                    
                    st.rerun()   # rerun the app to update the table
        
        
        
        @st.cache_data
        def convert_df_csv(df) -> bytes:
            # converts the dataframe to a csv file
            # IMPORTANT: Cache the conversion to prevent computation on every rerun
            return df.to_csv(index=False).encode("utf-8")

        csv = convert_df_csv(st.session_state.dataset)

        
        if st.download_button(label="Download modified dataset as CSV", data=csv,
                            file_name = st.session_state.file_name[:-4] + "_modified.csv", 
                            mime="text/csv", type="primary"):  # remove orignal file extension and add "_modified.csv" to the name
            st.success("Downloaded successfully!", icon="✅")
        
        
        
        
        
    else:
        st.write("Please, upload a file first...")