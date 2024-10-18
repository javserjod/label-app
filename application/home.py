import streamlit as st

def app():
    st.title("Welcome to Label App!")
    
    st.markdown('''
       
        ## Information
        Label App is a free, simple application designed to assist in manually editing, visualizing and labelling your moderate-sized datasets.

        The project is implemented in pure Python, using Streamlit framework with the special help of Pandas and Plotly libraries.

        ## Functionalities
        You will be able to:
        - Upload and preview your original dataset in any source extension of the supported: CSV, JSON, Excel and Parquet.
        - Modify the dataset with several tools as you visualize the changes: handle NA values, rename and displace headers, add and delete variables, replace cell values, insert new samples, sort by columns, control variables data types and filter with conditional statements.
        - Plot the dataset in a parameterized graph (line chart, scatter plot, bar chart) where you can draw by hand selectors to group samples and assign classes to them. The new label column can be added to the dataset and mantain the operational flow.
        - Check aditional information about the dataset: general description, histograms for each variable, boxplots where detect outliers, bubble chart, radar chart, parallel coordinates plot and correlation matrix.
        - Rename and download the modified dataset in one of the supported extensions.

        ## Access
        The app is reachable in the Streamlit Community Cloud: https://label-app-javserjod.streamlit.app/
        
        GitHub repository, where you can download the source code and run it locally: https://github.com/javserjod/label-app
        
        ## Author
        Developed by Javier Serrano Jodral as final project for Biomedical Engineering Master's Degree at Universidad de Sevilla.
                
    ''')
    