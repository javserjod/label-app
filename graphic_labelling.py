import streamlit as st
#import plotly.express as px     # necessary for the plotly chart (quick)
import plotly.graph_objects as go
import pandas as pd
from reset_functions import reset_all_session_state

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
        st.toggle("TIME SERIES?", help="Selecting this option will set a time axis given a selected frequency or column from dataset. If not selected, just represents variables against other variable.",
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
                    reload_line_chart_freq()   # reload and set time axis when loading (initialize)
                
                else:     # select one column as time axis
                    st.multiselect("Select the variable that contains the time axis", options=st.session_state.dataset.columns.tolist(),
                                max_selections=1, default=st.session_state.line_chart_time_column, on_change= reload_line_chart_time_column, key="multiselect_time_column")    # select the time column NAME
                    reload_line_chart_time_column()       # reload and set time axis when loading (initialize)
                
                # text input for line chart title
                st.session_state.line_chart_title=st.text_input("Title of the line chart:", value=st.session_state.line_chart_title, key="line_chart_text_input_title",
                              on_change=reload_line_chart_title)    # input for the name of the line chart

                # add traces to plot after given the parameters (time series)
                fig = go.Figure()
                for col in st.session_state.line_chart_y_axis:
                    fig.add_trace(go.Scatter(x=st.session_state.line_chart_time_axis, y=st.session_state.dataset.loc[:, col], name=col, 
                                             mode='lines+markers', marker={'opacity': 0}))   # line + markers mandatory for selection (markers opacity 0)
                
                fig.update_layout(title=dict(text=st.session_state.line_chart_title, x=0.5, xanchor='center', y=0.9, yanchor='top'), 
                                  xaxis_title=dict(text="Time (s)"), dragmode="select", selectdirection="h")
                                  #yaxis_title=dict(text=str(st.session_state.line_chart_y_axis)))    # set title and axis titles
                
                st.session_state.selected_data = st.plotly_chart(fig, key="data_selection_key", on_select="rerun")   # show and assign selection variable listening
                
                
            
            
                    
            else:    # not time series, just relation between continuos variables
                st.multiselect("Select the variable depicted in x-axis:", options=st.session_state.dataset.columns.tolist(),
                                max_selections=1, default=st.session_state.line_chart_column_against, on_change= reload_line_chart_column_against, key="multiselect_column_against")    # select the x-axis variable when no time series
                
                # text input for line chart title
                st.session_state.line_chart_title=st.text_input("Title of the line chart:", value=st.session_state.line_chart_title, key="line_chart_text_input_title",
                              on_change=reload_line_chart_title)    # input for the name of the line chart
                
                # add traces to plot after given the parameters (not time series)
                fig = go.Figure()
                for col in st.session_state.line_chart_y_axis:
                    fig.add_trace(go.Scatter(x=st.session_state.dataset.loc[:, st.session_state.line_chart_column_against[0]], y=st.session_state.dataset.loc[:, col], name=col, 
                                             mode='lines+markers', marker={'opacity': 0}))   # line + markers mandatory for selection (markers opacity 0)
                
                fig.update_layout(title=dict(text=st.session_state.line_chart_title, x=0.5, xanchor='center', y=0.9, yanchor='top'), 
                                  xaxis_title=dict(text=st.session_state.line_chart_column_against[0]),
                                  dragmode="select", selectdirection="h")
                                  #yaxis_title=dict(text=str(st.session_state.line_chart_y_axis)))    # set title and axis titles
                
                st.session_state.selected_data = st.plotly_chart(fig, key="data_selection_key", on_select="rerun")   # show and assign selection variable listening
        
        
            
        # LABELLING SECTION
            st.subheader("Labelling Section")
            
            #info about selected data samples interval
            try:
                interval=f"[{st.session_state.selected_data.selection.points[0]['point_index']}, {st.session_state.selected_data.selection.points[-1]['point_index']}]"
                txt = f"Selected data samples interval:\t{interval}"
                st.write(":white_check_mark: "+txt)
            except Exception:
                st.write(":question: No data samples interval selected on the graph...")
            
            # classes for labelling
            col1, col2= st.columns(2)
            with col2:  # add new class for label
                if st.text_input("Add all the possible classes for the label:", value="", placeholder="New class label",
                            on_change=add_new_class_label, key="new_class_label_key"):
                    if st.session_state.new_class_label_key in st.session_state.label_classes:   # if didn't empty in before function
                        st.error("The class already exists... Please, add a new one", icon="🚨")
                    if not any(char.isalnum() for char in st.session_state.new_class_label_key):
                        st.error("The class name must contain at least one alphanumeric character", icon="🚨")
                    
            with col1:  # currently activated class
                st.multiselect(f":label: Currently activated class:", options=st.session_state.label_classes,
                                placeholder="Select the activated class",
                                max_selections=1, default=st.session_state.currently_selected_class, on_change= reload_currently_activated_class, key="currently_selected_class_key")    # select the x-axis variable when no time series
            
            # button to apply the class to the samples
            if st.session_state.currently_selected_class != [] and st.session_state.selected_data.selection.points != []:   # if at least one sample is selected and a class is activated   
                if st.button(f"Confirm labelling of interval with activated class", on_click=label_selected_data):   # label selected data with activated class from label options
                        st.success("Success in labelling the selected data", icon="✅")
            else:
                st.button(f"Confirm labelling of interval with activated class", disabled=True,
                            help="Only clickable if a data samples interval is selected and a class for the label is activated")   # label selected data with activated class from label options
                    
            # default name variations if already used
            if st.session_state.label_column_name=="label_column" and "label_column" in st.session_state.dataset.columns.tolist():  
                st.session_state.label_column_name += "_" + str(len(st.session_state.dataset.columns))  # avoid duplicated column default name
            
            # preliminary labelled dataset as data editor
            st.session_state.labelled_dataset = st.data_editor(pd.concat([st.session_state.dataset, pd.DataFrame(st.session_state.label_column, columns=[st.session_state.label_column_name])], axis=1),
                                                                use_container_width = True)
            # text input for the name of the label column
            st.session_state.label_column_name = st.text_input("Label column name:", value=st.session_state.label_column_name, 
                                                                on_change=reload_label_column_name, key="label_column_name_key")
            if st.session_state.label_column_name_key in st.session_state.dataset.columns.tolist() or not any(char.isalnum() for char in st.session_state.label_column_name_key):
                st.error("Please, write a valid name for the label column... It can't be duplicated and must contain at least one alphanumeric character", icon="🚨")
    
            # save labels button
            if st.button("Save labels", on_click= save_labels):   # save changes: modify the dataset and show success message
                st.success("Labels saved successfully! Check the resulting dataset in Edit Data page", icon="✅") 

            
        except Exception as e:
            #st.error(e)
            st.error("Please, select correct parameters to plot the line chart... Problem: " + str(e), icon="🚨")    # if any error occurs, show message
        
    
    
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
            st.session_state.freq_aux = 1.00
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
    
    
    # labelling
    def add_new_class_label() -> None:
        # add a new label to the label classes
        if st.session_state.new_class_label_key not in st.session_state.label_classes:   # if not duplicated
            if any(char.isalnum() for char in st.session_state.new_class_label_key):  # if at least one alphanumeric character
                st.session_state.label_classes.append(st.session_state.new_class_label_key)
                st.session_state.new_class_label_key = ""        # empty the text input
        # else error message
        
    def reload_currently_activated_class() -> None:
        # reload the activated class
        st.session_state.currently_selected_class = st.session_state.currently_selected_class_key
    
    def label_selected_data() -> None:
        for point in st.session_state.selected_data.selection.points:
            st.session_state.label_column[point['point_index']] = st.session_state.currently_selected_class[0]    # label the selected data with the activated class
        
    def reload_label_column_name() -> None:
        # reload the name of the label column
        if st.session_state.label_column_name_key not in st.session_state.dataset.columns.tolist() and any(char.isalnum() for char in st.session_state.label_column_name_key):  # if not duplicated and at least one alphanumeric character
            st.session_state.label_column_name = st.session_state.label_column_name_key
        
        #else error message
            
    def save_labels() -> None:
        # save the labels in the dataset
        st.session_state.dataset = st.session_state.labelled_dataset
        reset_all_session_state()   # reset all charts and labelling variables from session state to default value
    
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
                                     mode='lines+markers', line={'width':0}, name= group if type(group) == str else str(group)))  # convert to string if not string
        
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