import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from scipy.stats.stats import kendalltau   # just for kendall correlation matrix

def app():
    
    #-------------------------- FUNCTIONS ---------------------------#
    def get_numerical_non_numerical_columns() -> tuple:
        # returns 2 lists with the names of the numerical columns and non numerical columns of the dataset in the current state
        numerical_types = ['int16', 'int32', 'int64', 'float16', 'float32', 'float64']
        numerical_columns = st.session_state.dataset.select_dtypes(include=numerical_types).columns
        non_numerical_columns = st.session_state.dataset.select_dtypes(exclude=numerical_types).columns
        return numerical_columns, non_numerical_columns
    
    def get_categorical_columns() -> list:
        # returns a list with the names of the categorical columns of the dataset in the current state
        return st.session_state.dataset.select_dtypes(include='object').columns
        
    def get_bool_columns() -> list:
        # returns a list with the names of the boolean columns of the dataset in the current state
        return st.session_state.dataset.select_dtypes(include=['bool']).columns
    
    def get_datetime_columns() -> list:
        # returns a list with the names of the datetime columns of the dataset in the current state
        datetime_types = ["datetime", "datetime64", "datetime64[ns]", "datetimetz"]
        return st.session_state.dataset.select_dtypes(include=datetime_types).columns
    
    
    @st.cache_data
    def get_corr_matrix(corr_method: str, toggle_bool: bool) -> go.Figure:
        # returns a plotly figure with the correlation matrix of the numerical variables (and bool if toggle_bool is True)
        numerical_columns, _ = get_numerical_non_numerical_columns()
        numerical_columns = numerical_columns.append(get_datetime_columns())     # all numerical: int, float and datetime columns
        # we are here if len of numerical + bool is >= 2
        if len(numerical_columns) < 2:    # needs the bool to activate
            if toggle_bool:    # add boolean columns to the correlation matrix
                bool_columns = get_bool_columns()
                numerical_columns = numerical_columns.append(bool_columns)
                dataset_corr = st.session_state.dataset[numerical_columns].copy()    # copy, don't act on the current dataset
                dataset_corr[bool_columns] = dataset_corr[bool_columns].astype(float)    # convert boolean columns to float
            else:  # less than 2 variables in total
                raise Exception("Not enough numerical variables to calculate the correlation matrix. Try adding the boolean variables")
        else:   # only numerical columns could work alone, but check if bool 
            if toggle_bool:    # add boolean columns to the correlation matrix
                bool_columns = get_bool_columns()
                numerical_columns = numerical_columns.append(bool_columns)
                dataset_corr = st.session_state.dataset[numerical_columns].copy()    # copy, don't act on the current dataset
                dataset_corr[bool_columns] = dataset_corr[bool_columns].astype(float)    # convert boolean columns to float
            else:
                dataset_corr = st.session_state.dataset[numerical_columns].copy()    # copy, don't act on the current dataset

        
        corr = dataset_corr[numerical_columns].corr(method=corr_method)

        fig = go.Figure(data=[go.Heatmap(   z=corr.values, 
                                            x=corr.columns, 
                                            y=corr.columns, 
                                            colorscale="rdbu")])
        if toggle_bool:
            fig.update_layout(title=dict(text=f"{corr_method.capitalize()} correlation matrix of numerical and boolean variables", x=0.5, xanchor='center', y=0.9, yanchor='top'))
        else:
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
    
    
       # HISTOGRAMS CATEGORICAL (OBJECT, BOOLEAN) VARIABLES
        with st.expander("Histograms of categorical variables"):     # all categorical variables (object, boolean)
            try:
                categorical_columns = get_categorical_columns().append(get_bool_columns())
                if len(categorical_columns)> 0:    # at least one categorical variable in the dataset
                    st.info("Showing histograms of categorical variables (dtypes object and boolean) with less than 300 unique values, in order to limit resource consumption", icon=":material/help_center:")
                    for var in categorical_columns:
                        if st.session_state.dataset[var].nunique() <= 300:      #limit resource consuming
                            fig = go.Figure(data=[go.Histogram(y=st.session_state.dataset[var])])   #HORIZONTAL HISTOGRAM
                            fig.update_layout(title=dict(text="Histogram of "+var, x=0.5, xanchor='center', y=0.9, yanchor='top'), 
                                            xaxis_title_text='Count', yaxis_title_text=var,  # set axis titles (horizontal histogram)
                                            bargap=0.1,   # add gap between bars (separate classes)
                                            activeselection=dict(fillcolor='pink', opacity=0.001))
                            st.markdown("######")   # add space between components
                            st.plotly_chart(fig, key="hist_"+var, on_select="rerun", config=config)
                        else:   # too many unique values
                            st.markdown("######")   # add space between components
                            st.warning(f"Variable \"{var}\" has too many unique values ({st.session_state.dataset[var].nunique()}) to plot its histogram")
                else:
                    st.warning("No categorical variables in the dataset to plot histograms")
            except Exception:
                st.warning("This dataset does not support histograms") 
        
        
        # HISTOGRAMS NUMERICAL INT, FLOAT VARIABLES
        with st.expander("Histograms of numerical integer and float variables"):     # all int, float variables
            try:
                numerical_columns, _ = get_numerical_non_numerical_columns()
                if len(numerical_columns)> 0:    # at least one numerical variable in the dataset
                    st.info("Showing histograms of numerical variables (dtypes int and float, with any bits)", icon=":material/help_center:")
                    for var in numerical_columns:
                        fig = go.Figure(data=[go.Histogram(x=st.session_state.dataset[var])])
                        fig.update_layout(title=dict(text="Histogram of "+var, x=0.5, xanchor='center', y=0.9, yanchor='top'), 
                                        yaxis_title_text='Count', xaxis_title_text=var,  # set axis titles
                                        bargap=0,   # gap between bars
                                        activeselection=dict(fillcolor='pink', opacity=0.001))
                        
                        st.markdown("######")   # add space between components
                        st.plotly_chart(fig, key="hist_"+var, on_select="rerun", config=config)
                else:
                    st.warning("No numerical variables in the dataset to plot histograms")
            except Exception:
                st.warning("This dataset does not support histograms")
                
     
        # HISTOGRAMS NUMERICAL DATETIME VARIABLES
        with st.expander("Histograms of numerical datetime variables"):     # all datetime variables
            try:
                datetime_columns= get_datetime_columns()
                if len(datetime_columns)> 0:    # at least one datetime variable in the dataset
                    st.info("Showing histograms of datetime variables (dtypes datetime, datetime64, datetime64[ns], datetimetz)", icon=":material/help_center:")
                    for var in datetime_columns:
                        fig = go.Figure(data=[go.Histogram(x=st.session_state.dataset[var])])
                        fig.update_layout(title=dict(text="Histogram of "+var, x=0.5, xanchor='center', y=0.9, yanchor='top'), 
                                        yaxis_title_text='Count', xaxis_title_text=var,  # set axis titles
                                        bargap=0,   # gap between bars
                                        activeselection=dict(fillcolor='pink', opacity=0.001))
                        
                        st.plotly_chart(fig, key="hist_"+var, on_select="rerun", config=config)
                else:
                    st.warning("No datetime variables in the dataset to plot histograms")
            except Exception:
                st.warning("This dataset does not support histograms")
        
        
        # BOXPLOTS NUMERICAL VARIABLES BY NON-NUMERICAL VARIABLES
        with st.expander("Boxplots of numerical variables by categorical variables"):      # only int, float variables
            numerical_columns, _ = get_numerical_non_numerical_columns()
            numerical_columns = numerical_columns.append(get_datetime_columns())         # all numerical: int, float and datetime columns
            categorical_columns = get_categorical_columns().append(get_bool_columns())    # categorical and boolean columns
            
            if len(categorical_columns) > 0:    # at least one numerical variable in the dataset
                try:
                    if st.session_state.dataset.shape[0] <= 5000:    # limit number of rows
                        st.selectbox("Choose a non-numerical column X-axis and color:", categorical_columns, 
                                    key="boxplot_selectbox_key", index=None, placeholder="Select a non-numerical variable",
                                    help="Choose a non-numerical column for X-axis and whose categories will color the boxplots for each numerical variable. Preferably a categorical variable with few unique values or a boolean one. Limit is set to 300 unique values")            
                    
                    
                        if st.session_state.boxplot_selectbox_key != None:    # if any categorical variable is selected
                            if st.session_state.dataset[st.session_state.boxplot_selectbox_key].nunique() <= 300:      #limit resource consuming
                                
                                    for var in numerical_columns:   # only numerical variables in the dataset have a boxplot
                                        fig = go.Figure()
                                        for var_class in st.session_state.dataset[st.session_state.boxplot_selectbox_key].unique():
                                            fig.add_trace(go.Box(   y=st.session_state.dataset[st.session_state.dataset[st.session_state.boxplot_selectbox_key]==var_class][var],    # unique values of categorical variable
                                                                    boxpoints="all",  # show all points
                                                                    jitter=0.5,    # spread points
                                                                    name=var_class if type(var_class) == str else str(var_class),
                                                                    boxmean='sd',  # show mean and standard deviation
                                                                    )
                                                            )
                                        fig.update_layout(title=dict(text="Boxplot of "+var+" by "+st.session_state.boxplot_selectbox_key, x=0.5, xanchor='center', y=0.9, yanchor='top'), 
                                                        dragmode="select", selectdirection="h",   # fits all height, just horizontal movement for selection
                                                        yaxis_title_text=var, xaxis_title_text=st.session_state.boxplot_selectbox_key,  # set axis titles
                                                        activeselection=dict(fillcolor='pink', opacity=0.001), showlegend=True)
                                        
                                        st.plotly_chart(fig, key="box_"+var, on_select="rerun", config=config)
                            else:
                                st.warning(f"Variable \"{st.session_state.boxplot_selectbox_key}\" has too many unique values ({st.session_state.dataset[st.session_state.boxplot_selectbox_key].nunique()}) to plot its histogram")       
                        else:
                            st.info("Select a non-numerical variable to color the boxplots. It must have no more than 300 unique classes", icon=":material/help_center:")
                    else:
                        st.warning("This dataset has too many rows to plot boxplots with current resources. Limit is 5000 samples")
                except Exception:
                    st.warning("This dataset does not support boxplots of numerical variables by non-numerical variables")
            else:
                st.warning("Zero non-numerical variables in the dataset")
        
        
        # CORRELATION MATRIX BETWEEN NUMERICAL VARIABLES
        with st.expander("Correlation matrix between numerical variables"):
            numerical_columns, _ = get_numerical_non_numerical_columns()
            numerical_columns = numerical_columns.append(get_datetime_columns())         # all numerical: int, float and datetime columns
            if len(numerical_columns) + len(get_bool_columns()) >= 2:    # at least two necessary
                col1, _, col2 = st.columns([3,1,3], vertical_alignment='bottom')
                with col1:
                    # method to calculate the correlation matrix
                    st.selectbox("Choose a correlation method", options=["pearson", "spearman", "kendall"], 
                                    key="corr_method_selectbox_key", index=0, help="Choose a method to calculate the correlation matrix")
                with col2:
                    # add bool variable toggle
                    if len(get_bool_columns()) >= 1:  # at least one bool to add
                        st.toggle("Add bool variables", key="add_bool_variables_toggle_key", value=False, help="Add boolean variables to the correlation matrix, which will be treated as numerical")
                    else:
                        st.toggle("Add bool variables", key="add_bool_variables_toggle_key", value=False, help="No boolean variables in the dataset to add to the correlation matrix",
                                  disabled=True)
                        #st.info("No boolean variables in the dataset to add to the correlation matrix", icon=":material/help_center:")
                try:
                    # show the correlation matrix
                    st.plotly_chart(get_corr_matrix(st.session_state.corr_method_selectbox_key, st.session_state.add_bool_variables_toggle_key), config=config)
                except Exception as e:
                    st.warning(str(e))
            else:
                st.warning("No correlation matrix to show. At least two valid variables are needed")
              

    else:
        st.info("Please, upload a file first", icon=":material/help_center:")    # if no file uploaded, show info message