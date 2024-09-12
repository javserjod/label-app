import streamlit as st

def app():
    
    if st.session_state.dataset is not None:   # if any data was uploaded
        st.write("Data Information Page")
    else:
        st.write("Please, upload a file first...")