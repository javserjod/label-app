import streamlit as st
#import plotly.express as px     # necessary for the plotly chart (quick)
import plotly.graph_objects as go

def app():
    
    #-------------------------- FUNCTIONS ---------------------------#
    
    def reload_graph_type_selectbox() -> None:
        # reload the graph type selectbox index since last selected option (graph_options defined in scope)
        st.session_state.graph_selectbox_index = graph_options.index(st.session_state.graph_type)    # store the index of selected graph type
        
    #......................LINE CHART...........................................
    def line_chart() -> None:
        # plot the data in a line chart
        st.subheader("Line Chart")
        
        # toggle for selecting if time series or not
        st.toggle("TIME SERIES?", help="Selecting this option will set a time axis given a selected frequency or column from dataset. If not selected, just represents variables against other variable",
                  value=st.session_state.line_chart_toggle_time_series, on_change=reload_line_chart_toggle_time_series)
        
        try:  
            # y axis data selection from dataset
            multiselect_col, add_button_col = st.columns([0.8, 0.2], vertical_alignment="bottom")
            with multiselect_col:
                st.multiselect("Select the data to be displayed in the line chart, on the y-axis:", options=st.session_state.dataset.columns.tolist(),
                        default = st.session_state.line_chart_y_axis, on_change=reload_line_chart_multiselect, key="line_chart_multiselect")    # multiselect for the columns to be displayed in the line chart
            with add_button_col:
                st.button("Add all columns", on_click=line_chart_add_all_columns)


            if st.session_state.line_chart_toggle_time_series:   # if toggle is selected, show options for time series (creating time axis) 
                # input for the frequency of the data, in Hertz
                st.toggle("Use sampling frequency to set time axis?", help="Selecting this option will set the time axis based on the sampling frequency of the data. If not selected, select one column from the dataset to be used as time axis.",
                            value=st.session_state.line_chart_toggle_time_axis, on_change=reload_line_chart_toggle_time_axis)
                
                if st.session_state.line_chart_toggle_time_axis:   # if toggle is selected, show the number input for the frequency
                    
                    st.number_input("Sampling frequency of the data in Hz:", value=st.session_state.freq_number_input, step=None, 
                                on_change=reload_line_chart_freq, key = "freq_aux")    # number input for the frequency of the data
                    reload_line_chart_freq()   # reload and set time axis when loading, although not changed number input
                
                else:     # select one column as time axis
                    st.multiselect("Select the variable that contains the time axis", options=st.session_state.dataset.columns.tolist(),
                                max_selections=1, default=st.session_state.line_chart_time_column, on_change= reload_line_chart_time_column, key="multiselect_time_column")    # select the time column NAME
                    reload_line_chart_time_column()       # reload and set time axis when loading, although not changed multiselect
                
                # text input for line chart title
                st.text_input("Title of the line chart:", value=st.session_state.line_chart_title, key="line_chart_text_input_title",
                              on_change=reload_line_chart_title)    # input for the name of the line chart

                # add traces to plot after given the parameters (time series)
                fig = go.Figure()
                for col in st.session_state.line_chart_y_axis:
                    fig.add_trace(go.Scatter(x=st.session_state.line_chart_time_axis, y=st.session_state.dataset.loc[:, col], mode='lines', name=col))
                
                fig.update_layout(title=dict(text=st.session_state.line_chart_title, x=0.5, xanchor='center', y=0.9, yanchor='top'), 
                                  xaxis_title=dict(text="Time (s)")),
                                  #yaxis_title=dict(text=str(st.session_state.line_chart_y_axis)))    # set title and axis titles
                
                st.session_state.selected_data = st.plotly_chart(fig)   # show and assign selection variable listening
            
            else:    # not time series, just relation between continuos variables
                st.multiselect("Select the variable depicted in x-axis:", options=st.session_state.dataset.columns.tolist(),
                                max_selections=1, default=st.session_state.line_chart_column_against, on_change= reload_line_chart_column_against, key="multiselect_column_against")    # select the x-axis variable when no time series
                
                # text input for line chart title
                st.text_input("Title of the line chart:", value=st.session_state.line_chart_title, key="line_chart_text_input_title",
                              on_change=reload_line_chart_title)    # input for the name of the line chart
                
                # add traces to plot after given the parameters (not time series)
                fig = go.Figure()
                for col in st.session_state.line_chart_y_axis:
                    fig.add_trace(go.Scatter(x=st.session_state.dataset.loc[:, st.session_state.line_chart_column_against[0]], y=st.session_state.dataset.loc[:, col], mode='lines', name=col))
                
                fig.update_layout(title=dict(text=st.session_state.line_chart_title, x=0.5, xanchor='center', y=0.9, yanchor='top'), 
                                  xaxis_title=dict(text=st.session_state.line_chart_column_against[0])),
                                  #yaxis_title=dict(text=str(st.session_state.line_chart_y_axis)))    # set title and axis titles
                
                st.session_state.selected_data = st.plotly_chart(fig)   # show and assign selection variable listening
                
        except:
                st.error("Please, select correct parameters to plot the line chart...", icon="🚨")    # if any error occurs, show message
        
    
    
    def line_chart_add_all_columns() -> None:
        st.session_state.line_chart_y_axis = st.session_state.dataset.columns.tolist()    # store all columns for the line chart
    
    def reload_line_chart_toggle_time_series() -> None:
        st.session_state.line_chart_toggle_time_series = not st.session_state.line_chart_toggle_time_series    # change the value of the toggle
        
    def reload_line_chart_multiselect() -> None:
        st.session_state.line_chart_y_axis = st.session_state.line_chart_multiselect    # store the selected columns for the line chart
    
    def reload_line_chart_toggle_time_axis() -> None:
        st.session_state.line_chart_toggle_time_axis = not st.session_state.line_chart_toggle_time_axis    # change the value of the toggle
        
    def reload_line_chart_freq() -> None:
        # reload variable storing frequency number input and set time axis since frequency
        st.session_state.freq_number_input = st.session_state.freq_aux
        try:
            dt = 1/st.session_state.freq_number_input     # time step (seconds)
        except ZeroDivisionError:
            st.error('Frequency can\'t be zero. Returning its value to 1...', icon="🚨")   # error
            st.session_state.freq_number_input = 1.00
            dt = 1/st.session_state.freq_number_input
        st.session_state.line_chart_time_axis = [i*dt for i in range(0, len(st.session_state.dataset))]  # values for the time axis
        
    def reload_line_chart_time_column() -> None:
        # reload the time axis column selected in the multiselect and set time axis since column name from dataset
        st.session_state.line_chart_time_column = st.session_state.multiselect_time_column
        st.session_state.line_chart_time_axis = st.session_state.dataset.loc[:, st.session_state.line_chart_time_column[0]]    # select the column from the dataset to be used as time axis
    
    def reload_line_chart_column_against() -> None:
        # reload the x axis variable selected in the multiselect when no time series
        st.session_state.line_chart_column_against = st.session_state.multiselect_column_against
        
    def reload_line_chart_title() -> None:
        # reload the title of the line chart
        st.session_state.line_chart_name = st.session_state.line_chart_text_input_title
    
    #.............................................................................



    #...................SCATTER PLOT..............................................
    def scatter_plot() -> None:
        # plot the data in a scatter plot
        st.subheader("Scatter Plot")
        
        st.selectbox("Select the x-axis:", st.session_state.dataset.columns.tolist(), index = st.session_state.scatter_x_axis_index,
                    on_change=reload_scatter_plot_x, key="x_axis")    # select the x axis data from index
        st.selectbox("Select the y-axis:", st.session_state.dataset.columns.tolist(), index = st.session_state.scatter_y_axis_index,
                    on_change=reload_scatter_plot_y, key="y_axis")    # select the y axis data from index
        st.selectbox("Select the color (usually a categorical column):", st.session_state.dataset.columns.tolist(),
                                    index = st.session_state.scatter_color_index, on_change=reload_scatter_plot_color, key="color")    # select the color data from index
        
        fig = go.Figure()
        
        groups = st.session_state.dataset[st.session_state.color].unique()   # different labels for the selected column
        for group in groups:    # add a trace for each label (if user selects non categorical column, there will be many traces)
            fig.add_trace(go.Scatter(x=st.session_state.dataset[st.session_state.dataset[st.session_state.color] == group][st.session_state.x_axis], 
                                     y=st.session_state.dataset[st.session_state.dataset[st.session_state.color] == group][st.session_state.y_axis], 
                                     mode='markers', name= group if type(group) == str else str(group)))
        
        st.session_state.selected_data = st.plotly_chart(fig)    # show and assign selection variable listening
    
        
    def reload_scatter_plot_x() -> None:
        # reload the index of column that will be used as x axis in scatter plot
        st.session_state.scatter_x_axis_index = st.session_state.dataset.columns.tolist().index(st.session_state.x_axis)
                
    def reload_scatter_plot_y() -> None:
        # reload the index of column that will be used as y axis in scatter plot
        st.session_state.scatter_y_axis_index = st.session_state.dataset.columns.tolist().index(st.session_state.y_axis)   
                
    def reload_scatter_plot_color() -> None:
        # reload the index of column that will be used as color in scatter plot
        st.session_state.scatter_color_index = st.session_state.dataset.columns.tolist().index(st.session_state.color)                           
    
    
    
    #...................BAR PLOT..............................................
    def bar_plot() -> None:        
           pass 
            
            
            
    #...................PIE PLOT..............................................        
    def pie_chart() -> None:
        pass
    
    
    
    
            
    #---------------------------- PAGE ------------------------------#
    if st.session_state.dataset is not None:   # if any data was uploaded
        st.header("Graphic Labelling")
        st.subheader(f"File name: {st.session_state.file_name}")
        
        graph_options = ["None", "Line Chart", "Scatter Plot", "Bar Chart", "Pie Chart"]   # all the graph types available
        st.selectbox("Graph type", graph_options, index = st.session_state.graph_selectbox_index,
                        on_change=reload_graph_type_selectbox, key="graph_type")    # select the graph type (index is preselected option)
        
        
        if st.session_state.graph_type == "None":     # nothing
            st.error("Select a graph type to show all its parameters and display the data...")
        with st.container(border = True):
            if st.session_state.graph_type == "Line Chart":
                line_chart()
            elif st.session_state.graph_type == "Scatter Plot":
                scatter_plot()
            elif st.session_state.graph_type == "Bar Chart":
                bar_plot()
            elif st.session_state.graph_type == "Pie Chart":    
                pie_chart()
                
    else:
        st.write("Please, upload a file first...")