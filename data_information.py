import streamlit as st

def app():
    
    if st.session_state.dataset is not None:   # if any data was uploaded
        st.header("Data Information")
        st.subheader(f"File name: {st.session_state.file_name}")
        st.write(":construction: This page is under construction. :construction:")
    else:
        st.warning("Please, upload a file first...")    # if no file uploaded, show warning message