import streamlit as st
import plotly.graph_objects as go

def app():
    
    config = {'displayModeBar': True,
                'toImageButtonOptions': {
                        'format': 'png', # one of png, svg, jpeg, webp
                        'filename': st.session_state.file_name+'_plot',
                        'height': 1080,
                        'width': 1920,
                        'scale': 5 # Multiply title/legend/axis/canvas sizes by this factor
                        }
                }
    
    
    
    if st.session_state.dataset is not None:   # if any data was uploaded
        st.header("Data Information")
        st.subheader(f"File name: {st.session_state.file_name}")
        st.write(":construction: This page is under construction. :construction:")
        
        for var in st.session_state.dataset.columns:
            '''if st.session_state.dataset[var].dtype == "object":
                st.write(f"Variable: {var}")
                st.write(f"Type: {st.session_state.dataset[var].dtype}")
                st.write(f"Unique values: {st.session_state.dataset[var].nunique()}")
                st.write(f"Missing values: {st.session_state.dataset[var].isnull().sum()}")
                st.write(f"Top 5 values: {st.session_state.dataset[var].value_counts().head()}")
                st.write("\n")'''
            
            
            fig = go.Figure(data=[go.Histogram(x=st.session_state.dataset[var])])
            #fig.show()
        
            st.plotly_chart(fig, key="info_"+var, on_select="rerun", config=config)
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
    else:
        st.warning("Please, upload a file first...")    # if no file uploaded, show warning message