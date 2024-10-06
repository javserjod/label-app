import streamlit as st
import plotly.graph_objects as go
import pandas as pd

def app():
    
    #-------------------------- FUNCTIONS ---------------------------#
    def get_numerical_non_numerical_columns() -> tuple:
        # returns 2 lists with the names of the numerical columns and non numerical columns of the dataset in the current state
        numerical_types = ['int16', 'int32', 'int64', 'float16', 'float32', 'float64']
        numerical_columns = st.session_state.dataset.select_dtypes(include=numerical_types).columns
        non_numerical_columns = st.session_state.dataset.select_dtypes(exclude=numerical_types).columns
        return numerical_columns, non_numerical_columns
    
    def get_bool_columns() -> list:
        # returns a list with the names of the boolean columns of the dataset in the current state
        bool_columns = st.session_state.dataset.select_dtypes(include=['bool']).columns
        return bool_columns
    
    @st.cache_data
    def get_corr_matrix(corr_method: str, toggle_bool: bool) -> go.Figure:
        # returns a plotly figure with the correlation matrix of the numerical variables
        numerical_columns_names, _ = get_numerical_non_numerical_columns()
        if toggle_bool:    # add boolean columns to the correlation matrix
            bool_columns = get_bool_columns()
            numerical_columns_names = numerical_columns_names.append(bool_columns)
        corr = st.session_state.dataset[numerical_columns_names].corr(method=corr_method)
        fig = go.Figure(data=[go.Heatmap(   z=corr.values, 
                                            x=corr.columns, 
                                            y=corr.columns, 
                                            colorscale="rdbu")])
        fig.update_layout(title=dict(text=f"{corr_method.capitalize()} correlation matrix of numerical variables", x=0.5, xanchor='center', y=0.9, yanchor='top'))
        fig.update_traces(text=corr.values.round(3), texttemplate="%{text}", hovertemplate=None)
        return fig
    
    
    #---------------------------- PAGE ------------------------------#
    
    if st.session_state.dataset is not None:   # if any data was uploaded
    
        config = {#'displayModeBar': True,   # show only on hover
                'toImageButtonOptions': {     # dowload image options
                        'format': 'png', # one of png, svg, jpeg, webp
                        'filename': st.session_state.file_name+'_plot',
                        'height': 1080,
                        'width': 1920,
                        'scale': 5 # Multiply title/legend/axis/canvas sizes by this factor
                        }
                }
        
        st.header("Data Information")
        st.subheader(f"File name: {st.session_state.file_name}")
        st.write("Click the expanders to show information about the dataset in the current state")
        st.markdown("######")   # add space between titles and the expanders
        

        # GENERAL DATASET DESCRIPTION
        with st.expander("General dataset description"):
            try:
                st.dataframe(st.session_state.dataset.describe(include="all").T,    # show all variables regardless of data type
                            use_container_width = True)
            except Exception:
                st.warning("Dataset has no columns to describe")
    
        
        # HISTOGRAMS EVERY VARIABLE
        with st.expander("Histograms of variables"):     # all variables
            try:
                if st.session_state.dataset.shape[1] > 0:    # at least one variable in the dataset
                    for var in st.session_state.dataset.columns:
                        fig = go.Figure(data=[go.Histogram(x=st.session_state.dataset[var])])
                        
                        fig.update_layout(title=dict(text="Histogram of "+var, x=0.5, xanchor='center', y=0.9, yanchor='top'), 
                                        yaxis_title_text='Frequency', xaxis_title_text=var,  # set axis titles
                                        #dragmode="select", selectdirection="h",   # fits all height, just horizontal movement for selection
                                        bargap=0.1,   # gap between bars
                                        activeselection=dict(fillcolor='pink', opacity=0.001))
                        
                        st.plotly_chart(fig, key="hist_"+var, on_select="rerun", config=config)
                else:
                    st.warning("No variables in the dataset to plot histograms")
            except Exception:
                st.warning("This dataset does not support histograms")
        
        
        # BOXPLOTS NUMERICAL VARIABLES BY NON-NUMERICAL VARIABLES
        with st.expander("Boxplots of numerical variables by non-numerical variables"):      # only numerical variables
            numerical_columns_names, non_numerical_columns_names = get_numerical_non_numerical_columns()
            if len(non_numerical_columns_names) > 0:    # at least one numerical variable in the dataset
                try:
                    st.selectbox("Choose a non-numerical column X-axis and color:", non_numerical_columns_names, 
                                 key="boxplot_selectbox_key", index=None, placeholder="Select a non-numerical variable",
                                 help="Choose a non-numerical column for X-axis and whose categories will color the boxplots for each numerical variable. Preferably a categorical variable with few unique values or a boolean one")            
                    
                    if st.session_state.boxplot_selectbox_key != None:    # if a non-numerical variable is selected
                        for var in numerical_columns_names:   # only numerical variables in the dataset have a boxplot
                            fig = go.Figure()
                            for var_class in st.session_state.dataset[st.session_state.boxplot_selectbox_key].unique():
                                fig.add_trace(go.Box(   y=st.session_state.dataset[st.session_state.dataset[st.session_state.boxplot_selectbox_key]==var_class][var],    # unique values of categorical variable
                                                        #y=st.session_state.dataset[var],
                                                        name=var_class if type(var_class) == str else str(var_class),
                                                        boxmean=True,  # show mean
                                                        )
                                                )
                            fig.update_layout(title=dict(text="Boxplot of "+var+" by "+st.session_state.boxplot_selectbox_key, x=0.5, xanchor='center', y=0.9, yanchor='top'), 
                                            dragmode="select", selectdirection="h",   # fits all height, just horizontal movement for selection
                                            yaxis_title_text=var, xaxis_title_text=st.session_state.boxplot_selectbox_key,  # set axis titles
                                            activeselection=dict(fillcolor='pink', opacity=0.001), showlegend=True)
                            
                            st.plotly_chart(fig, key="box_"+var, on_select="rerun", config=config)
                    else:
                        st.info("Select a non-numerical variable to color the boxplots", icon=":material/help_center:")
                except Exception:
                    st.warning("This dataset does not support boxplots of numerical variables by non-numerical variables")
            else:
                st.warning("Zero non-numerical variables in the dataset")
        
        
        # CORRELATION MATRIX BETWEEN NUMERICAL VARIABLES
        with st.expander("Correlation matrix between numerical variables"):
            numerical_columns_names, _ = get_numerical_non_numerical_columns()
            if len(numerical_columns_names) > 1:    # at least two numerical variables in the dataset
                col1, _, col2 = st.columns([3,1,3], vertical_alignment='bottom')
                with col1:
                    # method to calculate the correlation matrix
                    st.selectbox("Choose a correlation method", options=["pearson", "spearman", "kendall"], 
                                    key="corr_method_selectbox_key", index=0, help="Choose a method to calculate the correlation matrix")
                with col2:
                    st.toggle("Add bool variables", key="add_bool_variables_toggle_key", value=False, help="Add boolean variables to the correlation matrix, which will be treated as numerical")
                try:
                    # show the correlation matrix
                    st.plotly_chart(get_corr_matrix(st.session_state.corr_method_selectbox_key, st.session_state.add_bool_variables_toggle_key), config=config)
                except Exception:
                    st.warning("This dataset does not support this correlation matrix")
            else:
                st.warning("No correlation matrix to show. At least two numerical variables are needed")
    
    else:
        st.info("Please, upload a file first", icon=":material/help_center:")    # if no file uploaded, show info message