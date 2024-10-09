import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from reset_functions import reset_all_session_state


def app():
    
    #-------------------------- COMMON FUNCTIONS FOR EVERY CHART---------------------------#
    
    def reload_graph_type_selectbox() -> None:
        # reload the graph type selectbox index since last selected option (graph_options defined in scope)
        st.session_state.graph_selectbox_index = graph_options.index(st.session_state.graph_type)    # store the index of selected graph type
        reset_all_session_state()   # reset all charts and labelling variables from session state to default value
        
    def reload_chart_title() -> None:
        # reload the title of a chart from its text input
        st.session_state.chart_name = st.session_state.chart_text_input_title
        
    def reload_chart_toggle_color() -> None:
        # reload the toggle for showing colors in a chart
        st.session_state.chart_toggle_color = not st.session_state.chart_toggle_color    # change the value of the toggle
        
    def reload_color_picker() -> None:
        # reload the color picker for the activated class
        st.session_state.color_picker = st.session_state.color_picker_key
        
    def reload_multiselect_y_axis_variable() -> None:
        # reload the selected columns for the y axis in a multiselect
        st.session_state.multiselect_y_axis_variable = st.session_state.multiselect_y_axis_variable_key    # store the selected columns
        
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
    
    def delete_classes_options() -> None:
        # delete classes options and remove the activated class
        st.session_state.label_classes = []
        st.session_state.currently_selected_class = []    
        
    def reload_label_column_name() -> None:
        # reload the name of the label column
        if st.session_state.label_column_name_key not in st.session_state.dataset.columns.tolist() and any(char.isalnum() for char in st.session_state.label_column_name_key):  # if not duplicated and at least one alphanumeric character
            st.session_state.label_column_name = st.session_state.label_column_name_key
        #else error message
            
    def save_labels() -> None:
        # save the labels in the dataset
        if st.session_state.graph_type == "Line Chart":    # show on the top of page the success message, because on the bottom is not possible due to the exception caused by the reset of multiselect
            st.success("Labels saved successfully! Check the resulting dataset in Edit Data page", icon="✅")
        st.session_state.dataset = st.session_state.labelled_dataset
        reset_all_session_state()   # reset all charts and labelling variables from session state to default value
        
    #......................LINE CHART...........................................
    def line_chart() -> None:
        # plot the data in a line chart
        st.subheader("Line Chart")
        
        # toggle for selecting if time series or not
        st.toggle("TIME SERIES?", help="Selecting this option will set a time axis given a selected frequency or column from dataset. If not selected, just represents variables against other variable",
                  value=st.session_state.line_chart_toggle_time_series, on_change=reload_line_chart_toggle_time_series)
        
        try:  
            # y axis data selection from dataset
            col1, col2 = st.columns([0.8, 0.2], vertical_alignment="bottom")
            with col1:
                st.multiselect("Select variables on the y-axis:", options=st.session_state.dataset.columns.tolist(),
                        default = st.session_state.multiselect_y_axis_variable, on_change=reload_multiselect_y_axis_variable, key="multiselect_y_axis_variable_key",    # multiselect for the columns to be displayed in the line chart
                        placeholder="Choose one or more options")
            with col2:
                st.button("Add all columns", on_click=line_chart_add_all_columns, use_container_width=True, 
                          help="Shortcut to add all the columns to the line chart")    # select all the variables in the multiselect

            if st.session_state.line_chart_toggle_time_series:   # if time series (creating time axis) 
                # input for the frequency of the data, in Hertz
                st.toggle("Use sampling frequency to set time axis?", help="Selecting this option will set the time axis based on the sampling frequency of the data. If not selected, select one column from the dataset to be used as time axis. On change, reset frequency and time axis column",
                            value=st.session_state.line_chart_toggle_time_axis, on_change=reload_line_chart_toggle_time_axis)
                
                if st.session_state.line_chart_toggle_time_axis:   # if toggle is selected, show the number input for the frequency
                    st.session_state.freq_number_input = st.number_input("Sampling frequency of the data in Hz:", value=st.session_state.freq_number_input, step=None, 
                                on_change=reload_line_chart_freq, key = "freq_aux")    # number input for the frequency of the data
                    reload_line_chart_freq()   # reload and set time axis when loading (initialize)
                
                else:     # select one column as time axis
                    if len(st.session_state.line_chart_time_column) == 1:    # if selected
                        if not st.multiselect("Select the variable that contains the time axis", options=st.session_state.dataset.columns.tolist(),
                                    max_selections=1, default=st.session_state.line_chart_time_column, on_change= reload_line_chart_time_column, key="multiselect_time_column"):    # select the time column NAME
                            reload_line_chart_time_column()       # reload and set time axis when loading (initialize)
                    else:
                        st.multiselect("Select the variable that contains the time axis", options=st.session_state.dataset.columns.tolist(),
                                    max_selections=1, default=st.session_state.line_chart_time_column, on_change= reload_line_chart_time_column, key="multiselect_time_column")
                        if len(st.session_state.multiselect_y_axis_variable) > 0:
                            raise Exception("Time column missing")
                        else:
                            raise Exception("At least one Y-axis column and Time column are missing")
                
                # text input for line chart title
                st.session_state.chart_title=st.text_input("Title of the line chart:", value=st.session_state.chart_title, key="chart_text_input_title",
                              on_change=reload_chart_title, placeholder="No title")    # input for the name of the line chart

                # add traces to plot after given the parameters (time series)
                if len(st.session_state.multiselect_y_axis_variable) > 0:    # if at least one column is selected
                    global fig
                    fig = go.Figure()
                    for col in st.session_state.multiselect_y_axis_variable:
                        fig.add_trace(go.Scatter(x=st.session_state.line_chart_time_axis, 
                                                 y=st.session_state.dataset.loc[:, col], 
                                                 name=col, 
                                                 mode='lines+markers', marker={'opacity': 0}))   # line + markers mandatory for selection (markers opacity 0)
                    
                    fig.update_layout(title=dict(text=st.session_state.chart_title, x=0.5, xanchor='center', y=0.9, yanchor='top'), 
                                    xaxis_title=dict(text="Time (s)") if st.session_state.line_chart_toggle_time_axis else dict(text="Time : " +st.session_state.line_chart_time_column[0]), 
                                    dragmode="select", selectdirection="h",
                                    hovermode="x unified",        # assist for aiming samples
                                    activeselection=dict(fillcolor='pink', opacity=0.001), showlegend=True)
                                    #yaxis_title=dict(text=str(st.session_state.multiselect_y_axis_variable)))    # don't set y axis title - legend is preferred
                    
                    if st.session_state.chart_toggle_color:   # if toggle is selected, show the colors
                        # add color shapes
                        for prev_sel in st.session_state.line_chart_painting_time_series:   # newest appears in foreground layer
                            fig.add_vrect(x0=prev_sel[0], x1=prev_sel[1], 
                                            annotation_text=prev_sel[2], annotation_position="top left", annotation_textangle=90,
                                            annotation_font_size=18, annotation_font_color="white", annotation_font_weight=600,
                                            line_width=0, fillcolor=prev_sel[3], opacity=1, layer="below")   # add colored rectangle for each label
                            
                    st.session_state.selected_data = st.plotly_chart(fig, key="data_selection_key", on_select="rerun", config=config)   # show and assign selection variable listening
                else:
                    raise Exception("No data selected for the y-axis")    # if no data selected for the y-axis, raise exception
                    
            else:    # not time series, just relation between continuous variables
                st.multiselect("Select the variable depicted in x-axis:", options=st.session_state.dataset.columns.tolist(),
                                max_selections=1, default=st.session_state.line_chart_column_against, on_change= reload_line_chart_column_against, key="multiselect_column_against")    # select the x-axis variable when no time series
                
                # text input for line chart title
                st.session_state.chart_title=st.text_input("Title of the line chart:", value=st.session_state.chart_title, key="chart_text_input_title",
                            on_change=reload_chart_title, placeholder="No title")    # input for the name of the line chart
                try:
                    # add traces to plot after given the parameters (not time series)
                    fig = go.Figure()
                    for col in st.session_state.multiselect_y_axis_variable:            
                            fig.add_trace(go.Scatter(x=st.session_state.dataset.loc[:, st.session_state.line_chart_column_against[0]], 
                                                     y=st.session_state.dataset.loc[:, col], 
                                                     name=col, 
                                                     mode='lines+markers', marker={'opacity': 0}))   # line + markers mandatory for selection (markers opacity 0)
                    
                    fig.update_layout(title=dict(text=st.session_state.chart_title, x=0.5, xanchor='center', y=0.9, yanchor='top'), 
                                    xaxis_title=dict(text=st.session_state.line_chart_column_against[0]),
                                    dragmode="select", selectdirection="h",
                                    hovermode="x unified",        # assist for aiming samples
                                    activeselection=dict(fillcolor='pink', opacity=0.001), showlegend=True)
                                    #yaxis_title=dict(text=str(st.session_state.multiselect_y_axis_variable)))    # don't set y axis title - legend is preferred
                    
                    if st.session_state.chart_toggle_color:   # if toggle is selected, show the colors
                        # add color shapes
                        for prev_sel in st.session_state.line_chart_painting_against:   # newest appears in foreground layer
                            fig.add_vrect(x0=prev_sel[0], x1=prev_sel[1], annotation_text=prev_sel[2], annotation_position="top left", annotation_textangle=90,
                                            annotation_font_size=18, annotation_font_color="white", annotation_font_weight=600,
                                            line_width=0, fillcolor=prev_sel[3], opacity=1, layer="below")   # add colored rectangle for each label
                    
                    st.session_state.selected_data = st.plotly_chart(fig, key="data_selection_key", on_select="rerun", config=config)   # show and assign selection variable listening
                except:
                    raise Exception("X-axis variable missing")    # if any error occurs (no x-axis variable), raise exception
            
            
        # LABELLING SECTION
            st.subheader("Labelling Section")
            
            # info about selected data samples interval
            try:
                if st.session_state.line_chart_toggle_time_series:   # if time series
                    if st.session_state.line_chart_toggle_time_axis:      # if using sampling frequency
                        interval=f"[{st.session_state.selected_data.selection.points[0]['point_index']}, {st.session_state.selected_data.selection.points[-1]['point_index']}]"
                        interval_time=f"[{st.session_state.selected_data.selection.points[0]['point_index']/st.session_state.freq_number_input:.2f}, {st.session_state.selected_data.selection.points[-1]['point_index']/st.session_state.freq_number_input:.2f}]"
                        txt = f"Selected samples interval (indexes): {interval} ---- Interval in seconds: {interval_time}"
                    else:
                        interval=f"[{st.session_state.selected_data.selection.points[0]['point_index']}, {st.session_state.selected_data.selection.points[-1]['point_index']}]"
                        interval_time=f"[{min(point['x'] for point in st.session_state.selected_data.selection.points)}, {max(point['x'] for point in st.session_state.selected_data.selection.points)}]"
                        txt = f"Selected samples interval (indexes): {interval} ---- Time interval: {interval_time}"
                else:
                    interval=f"[{min(point['x'] for point in st.session_state.selected_data.selection.points)}, {max(point['x'] for point in st.session_state.selected_data.selection.points)}]"
                    txt = f"Selected X axis interval:\t{interval}"
                txt=":white_check_mark: "+txt
            except Exception:
                txt=":question: No data samples selected on the graph..."
            
            with st.expander(txt, expanded=False):
                st.write(st.session_state.selected_data.selection.points)
                
            # classes for labelling
            col1, col2, col3 = st.columns([1, 1, 1], vertical_alignment="bottom")
            with col2:  # add new class for label
                if st.text_input(":heavy_plus_sign: Add classes for the label:", value="", placeholder="New class for the label",
                            on_change=add_new_class_label, key="new_class_label_key"):
                    if st.session_state.new_class_label_key in st.session_state.label_classes:   # if didn't empty in before function
                        st.error("The class already exists... Please, add a new one", icon="🚨")
                    if not any(char.isalnum() for char in st.session_state.new_class_label_key):
                        st.error("The class name must contain at least one alphanumeric character", icon="🚨")
                    
            with col1:  # currently activated class
                st.multiselect(f":label: Activated class:", options=st.session_state.label_classes,
                                placeholder="Select the activated class",
                                max_selections=1, default=st.session_state.currently_selected_class, on_change= reload_currently_activated_class, key="currently_selected_class_key")    # select the x-axis variable when no time series
            
            with col3:
                st.button(":wastebasket: Delete classes options", on_click= delete_classes_options,
                          use_container_width=True,
                          help="Delete from the activated class selector all the classes added before")    # delete all classes options


            _, col1, col2 = st.columns([0.22, 0.5, 1], vertical_alignment="bottom")
            with col1:
                st.session_state.color_picker = st.color_picker("Color:", value=st.session_state.color_picker,
                                on_change=reload_color_picker, key="color_picker_key",
                                help="Choose the color that will fill the next area selected on the graph")    # color picker for the activated class        
            with col2:
                st.toggle(":eye: Show the colors of the classes on the graph", value=st.session_state.chart_toggle_color, on_change=reload_chart_toggle_color,
                          help="Selecting this option will show the colors of the classes in the line chart")    # toggle for showing colors in the line chart

            if len(st.session_state.label_column) < 1:   # bug fix (error after resetting session state, when already labelled and change from edit Edit Data to Graphic Labelling)
                    st.session_state.label_column = [""]*st.session_state.dataset.shape[0]
                    
            # button to apply the class to the samples
            if st.session_state.currently_selected_class != [] and st.session_state.selected_data.selection.points != []:   # if at least one sample is selected and a class is activated   
                if st.button(f"Confirm preview of labelling for selected samples with activated class", on_click=label_selected_data_line_chart,
                             type="primary", use_container_width=True):   # label selected data with activated class from label options
                    st.success("Success in labelling the selected data", icon="✅")            
            else:
                st.button(f"Confirm preview of labelling for selected samples with activated class", disabled=True, type="primary",
                            use_container_width=True,
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
            st.button("Save labels", on_click=save_labels, type="primary", use_container_width=True)   # save changes: modify the dataset and show success message
                 # success message inside the callback (shows on the top of the page)
            
        except Exception as e:
            #st.error(e)
            st.error("Please, select correct parameters to plot the line chart... Problem: " + str(e), icon="🚨")    # if any error occurs, show message
        
    
    
    def line_chart_add_all_columns() -> None:
        st.session_state.multiselect_y_axis_variable = st.session_state.dataset.columns.tolist()    # store all columns for the line chart
    
    def reload_line_chart_toggle_time_series() -> None:
        st.session_state.line_chart_toggle_time_series = not st.session_state.line_chart_toggle_time_series
        # decided not to reset session state variables
    
    def reload_line_chart_toggle_time_axis() -> None:
        st.session_state.line_chart_toggle_time_axis = not st.session_state.line_chart_toggle_time_axis    # change the value of the toggle
        # also reload the chart when changing the toggle
        if st.session_state.line_chart_toggle_time_axis:
            st.session_state.freq_aux = st.session_state.freq_number_input    # force to run the reload function
            reload_line_chart_freq()
        else:
            if len(st.session_state.line_chart_time_column) == 1:    # if already one added
                st.session_state.multiselect_time_column = st.session_state.line_chart_time_column    # force to run the reload function
                reload_line_chart_time_column()
        
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
        try:
            st.session_state.line_chart_time_axis = st.session_state.dataset.loc[:, st.session_state.line_chart_time_column[0]]    # select the column from the dataset to be used as time axis
        except:
            pass
    
    def reload_line_chart_column_against() -> None:
        # reload the x axis variable selected in the multiselect when no time series
        st.session_state.line_chart_column_against = st.session_state.multiselect_column_against
        
    def label_selected_data_line_chart() -> None:
        # label the selected data with the activated class and add color shape to plot in line chart
        # label data (preliminary, so the dataset in Edit Data is not modified)
        for point in st.session_state.selected_data.selection.points:
            st.session_state.label_column[point['point_index']] = st.session_state.currently_selected_class[0]    # label the selected data with the activated class
        
        # add info for colored rectangle to plot next time
        if st.session_state.line_chart_toggle_time_series:   # if time series
            st.session_state.line_chart_painting_time_series.append([st.session_state.line_chart_time_axis[st.session_state.selected_data.selection.points[0]['point_index']], 
                                                                    st.session_state.line_chart_time_axis[st.session_state.selected_data.selection.points[-1]['point_index']], 
                                                                    st.session_state.currently_selected_class[0],
                                                                    st.session_state.color_picker])
        else:    # not time series
            st.session_state.line_chart_painting_against.append([min(point['x'] for point in st.session_state.selected_data.selection.points), 
                                                                max(point['x'] for point in st.session_state.selected_data.selection.points), 
                                                                st.session_state.currently_selected_class[0],
                                                                st.session_state.color_picker])
            
        st.success("Showing preliminary labelling on the graph and in the table below", icon="✅")    # success message

    #.............................................................................



    #...................SCATTER PLOT..............................................
    def scatter_plot() -> None:
        # plot the data in a scatter plot
        st.subheader("Scatter Plot")
        
        try:
            st.selectbox("Select the x-axis:", st.session_state.dataset.columns.tolist(), index = st.session_state.x_axis_variable_index,
                        on_change=reload_x_axis_variable_index, key="x_axis")    # select the x axis data from index
            
            st.selectbox("Select the y-axis:", st.session_state.dataset.columns.tolist(), index = st.session_state.y_axis_variable_index,
                        on_change=reload_y_axis_variable_index, key="y_axis")    # select the y axis data from index
            
            col1, col2 = st.columns([1, 1.5], vertical_alignment="bottom")
            with col1:
                st.toggle("Use new label column as color?", help="Selecting this will set the colors of the samples in the graph depending of the classes assigned to them. If not selected, use an existing variable for colouring",
                            value=st.session_state.toggle_color_label_variable, on_change=reload_toggle_color_label_variable)
            with col2:
                if st.session_state.toggle_color_label_variable:   # if toggle selected, use new label column as color
                    st.selectbox("Select the color (usually a categorical column):", st.session_state.dataset.columns.tolist(),
                                index = st.session_state.chart_color_variable_index, on_change=reload_chart_color_variable_index, key="color",
                                disabled=True)    # disabled selectbox if using new label column as color   
                else: 
                    st.selectbox("Select the color (usually a categorical column):", st.session_state.dataset.columns.tolist(),
                                index = st.session_state.chart_color_variable_index, on_change=reload_chart_color_variable_index, key="color")    # select the color data from index
            
            
            # text input for scatter plot chart title
            st.session_state.chart_title=st.text_input("Title of the scatter plot:", value=st.session_state.chart_title, key="chart_text_input_title",
                            on_change=reload_chart_title, placeholder="No title")    # input for the name of the scatter plot chart
            
            
            fig = go.Figure()
            
            if len(st.session_state.label_column) < 1:   # bug fix (error after resetting session state, when already labelled and change from edit Edit Data to Graphic Labelling)
                    st.session_state.label_column = [""]*st.session_state.dataset.shape[0]
                    
            if st.session_state.toggle_color_label_variable:   # if toggle is selected, use new label column as color   
                groups = list(set(st.session_state.label_column))    # minimun 1 group, the empty string
                for group in groups:    # add a trace for each label (if user selects non categorical column, there will be many traces)
                    idx_group = [index for index,value in enumerate(st.session_state.label_column) if value == group]    # indexes of samples labelled with the same class
                    
                    # colouring according to class
                    current_color = "grey"    # default color
                    if st.session_state.chart_toggle_color:   # if toggle is selected, show the colors
                        for cls, color in st.session_state.list_color_classes:    # check the color of the current class
                            if cls == group:
                                current_color = color
    
                    x_values=st.session_state.dataset.iloc[idx_group][st.session_state.x_axis]
                    y_values=st.session_state.dataset.iloc[idx_group][st.session_state.y_axis]
                    fig.add_trace(go.Scatter(x=x_values, 
                                                y=y_values, 
                                                mode='lines+markers', line={'width':0}, name= group if type(group) == str else str(group),     # convert to string if not string
                                                marker={'color': current_color},    # assign the samples the color of the class
                                                customdata=idx_group,        # to keep original indexes of the samples even after adding them to new curves/classes
                                                hoverinfo='text',
                                                hovertext=[f'Index: {idx}<br>X: {x}<br>Y: {y}<br>Class: {group}' for idx, x, y in zip(idx_group, x_values, y_values)],   # show the index of the sample when hovering (the top one if coinciding coordenates)
                                            )
                                  )    

            else:       # existing variable as color (NEW LABEL DOES NOT COLOUR POINTS)
                groups = st.session_state.dataset[st.session_state.color].unique()   # different labels for the selected column
                color_column = st.session_state.dataset[st.session_state.color]
                for group in groups:    # add a trace for each label (if user selects non categorical column, there will be many traces)
                    
                    idx_group = [index for index,value in enumerate(color_column) if value == group]    # indexes of samples labelled with the same class
                    
                    x_values=st.session_state.dataset.iloc[idx_group][st.session_state.x_axis]
                    y_values=st.session_state.dataset.iloc[idx_group][st.session_state.y_axis]
                    fig.add_trace(go.Scatter(x=x_values, 
                                                y=y_values, 
                                                mode='lines+markers', line={'width':0}, name= group if type(group) == str else str(group),    # convert to string if not string
                                                customdata=idx_group,        # to keep original indexes of the samples even after adding them to new curves/classes
                                                hoverinfo='text',
                                                hovertext=[f'Index: {idx}<br>X: {x}<br>Y: {y}<br>Class: {group}' for idx, x, y in zip(idx_group, x_values, y_values)],   # show the index of the sample when hovering (the top one if coinciding coordenates)
                                            )
                                  )  
                
            fig.update_layout(title=dict(text=st.session_state.chart_title, x=0.5, xanchor='center', y=0.9, yanchor='top'), 
                                xaxis_title=dict(text=st.session_state.dataset.columns.tolist()[st.session_state.x_axis_variable_index]),
                                yaxis_title=dict(text=st.session_state.dataset.columns.tolist()[st.session_state.y_axis_variable_index]),
                                dragmode="lasso",
                                activeselection=dict(fillcolor='pink', opacity=0.001), showlegend=True,
                                hovermode="closest")    # show the closest point when hovering
             
            
            st.session_state.selected_data = st.plotly_chart(fig, key="data_selection_key", on_select="rerun", config=config)    # show and assign selection variable listening


            # LABELLING SECTION
            st.subheader("Labelling Section")
            
            # info about selected data samples
            try: 
                n_points=f"{len(st.session_state.selected_data.selection.points)}"
                txt = f":white_check_mark: Points selected:\t{n_points}"
            except Exception:
                txt=":question: No data samples selected on the graph..."
                
            with st.expander(txt, expanded=False):
                st.write(st.session_state.selected_data.selection.points)
            
            # classes for labelling
            col1, col2, col3 = st.columns([1, 1, 1], vertical_alignment="bottom")
            with col2:  # add new class for label
                if st.text_input(":heavy_plus_sign: Add classes for the label:", value="", placeholder="New class for the label",
                            on_change=add_new_class_label, key="new_class_label_key"):
                    if st.session_state.new_class_label_key in st.session_state.label_classes:   # if didn't empty in before function
                        st.error("The class already exists... Please, add a new one", icon="🚨")
                    if not any(char.isalnum() for char in st.session_state.new_class_label_key):
                        st.error("The class name must contain at least one alphanumeric character", icon="🚨")
                    
            with col1:  # currently activated class
                st.multiselect(f":label: Activated class:", options=st.session_state.label_classes,
                                placeholder="Select the activated class",
                                max_selections=1, default=st.session_state.currently_selected_class, on_change= reload_currently_activated_class, key="currently_selected_class_key")
            
            with col3:
                st.button(":wastebasket: Delete classes options", on_click= delete_classes_options,
                          use_container_width=True,
                          help="Delete from the activated class selector all the classes added before")    # delete all classes options

            if st.session_state.toggle_color_label_variable:    # only if color is new label column
                try:
                    if st.session_state.currently_selected_class[0] not in st.session_state.label_column:
                        st.write(":eight_spoked_asterisk: New class selected. Choose its color in the color picker")
                    else:
                        st.write(":eight_pointed_black_star: Class already exists, so it has a color assigned")
                except:
                    st.write(":x: No class selected")
                
                _, col1, col2 = st.columns([0.22, 0.5, 1], vertical_alignment="bottom")
                with col1:
                    st.session_state.color_picker = st.color_picker("Color:", value=st.session_state.color_picker,
                                        on_change=reload_color_picker, key="color_picker_key",
                                        help="Choose the color that will identify the new class. If the class was already added, the previous color will remain...")    # color picker for the activated class        
    
                with col2:
                    st.toggle(":eye: Show the colors of the classes on the graph", value=st.session_state.chart_toggle_color, on_change=reload_chart_toggle_color,
                                help="Selecting this option will show the colors of the classes in the line chart. Otherwise, everyone is grey")    # toggle for showing colors in the line chart


            # button to apply the class to the samples
            if st.session_state.currently_selected_class != [] and st.session_state.selected_data.selection.points != []:   # if at least one sample is selected and a class is activated   
                if st.button(f"Confirm preview of labelling for selected samples with activated class", on_click=label_selected_data_scatter_plot,
                                type="primary", use_container_width=True):   # label selected data with activated class from label options
                    st.success("Showing preliminary labelling on the graph and in the table below", icon="✅")            
            else:   # disabled button, just to denote blockage
                st.button(f"Confirm preview of labelling for selected samples with activated class", disabled=True, type="primary",
                            help="Only clickable if any data sample is selected and a class for the label is activated",
                            use_container_width=True) 
        
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

            # save labels button (initially there was a on_click callback, but a problem with the label column made it not work after labelling)
            if st.button("Save labels", on_click=save_labels, type="primary",
                         use_container_width=True):   # save changes: modify the dataset and show success message
                st.success("Labels saved successfully! Check the resulting dataset in Edit Data page", icon="✅") 
                
        except Exception as e:
            #st.error(e)
            st.error("Please, select correct parameters to draw the scatter plot... Problem: " + str(e), icon="🚨")    # if any error occurs, show message
        
      
    def reload_x_axis_variable_index() -> None:
        # reload the index of column that will be used as x axis
        st.session_state.x_axis_variable_index = st.session_state.dataset.columns.tolist().index(st.session_state.x_axis)
                
    def reload_y_axis_variable_index() -> None:
        # reload the index of column that will be used as y axis
        st.session_state.y_axis_variable_index = st.session_state.dataset.columns.tolist().index(st.session_state.y_axis)   
    
    def reload_toggle_color_label_variable() -> None:
        # reload the toggle for using a new label column as color
        st.session_state.toggle_color_label_variable = not st.session_state.toggle_color_label_variable    # change the value of the toggle            
    
    def reload_chart_color_variable_index() -> None:
        # reload the index of column that will be used as color
        st.session_state.chart_color_variable_index = st.session_state.dataset.columns.tolist().index(st.session_state.color)                           
    
    
    def label_selected_data_scatter_plot() -> None:
        # label the selected data with the activated class and add info to variable that draws color polygon shape in scatter plot
        # check before adding
        if st.session_state.toggle_color_label_variable:      # if new label is color
            if st.session_state.currently_selected_class[0] not in st.session_state.label_column:   # if first time a class is added, assign the chosen color to it
                st.session_state.list_color_classes.append([st.session_state.currently_selected_class[0], st.session_state.color_picker])
            
        for point in st.session_state.selected_data.selection.points:
            st.session_state.label_column[point['customdata']] = st.session_state.currently_selected_class[0]    # label the selected samples with the activated class, keeping original indexes
            
        
        
            
    #...................BAR PLOT..............................................
    def bar_chart() -> None:        
        st.subheader("Bar Chart")
        
        try:
            # selectbox for the x axis variable
            st.selectbox("Select the x-axis variable:", st.session_state.dataset.columns.tolist(), index = st.session_state.x_axis_variable_index,
                        on_change=reload_x_axis_variable_index, key="x_axis", placeholder="Choose one x-axis variable")    # select the x axis data from index
            
            # selectbox for the color variable
            st.selectbox("Select the color (usually a categorical column):", st.session_state.dataset.columns.tolist(), placeholder="Choose one color variable",
                        index = st.session_state.chart_color_variable_index, on_change=reload_chart_color_variable_index, key="color")    # select the color data from index
            
            # selectbox for the barmode
            st.selectbox("Select the barmode:", ["group", "stack", "overlay"], index = st.session_state.barmode_index,
                         on_change=reload_barmode_index, key="barmode_key",
                         help="Group: side by side || Stack: stacked bars adding their heights || Overlay: overlaid bars")    # select the barmode
            
            # text input for scatter plot chart title
            st.session_state.chart_title=st.text_input("Title of the scatter plot:", value=st.session_state.chart_title, key="chart_text_input_title",
                            on_change=reload_chart_title, placeholder="No title")    # input for the name of the scatter plot chart
            
            # raise errors if values not selected
            if st.session_state.x_axis_variable_index == None:
                raise Exception("X-axis variable not selected")
            if st.session_state.chart_color_variable_index == None:
                raise Exception("Color variable not selected")
                
            
            fig = go.Figure(
                layout=dict(
                    barcornerradius=15)
                )
            
            st.session_state.translated_indexes = []   # list of translated indexes for each bar (empty at first)
            
            diff_colors= st.session_state.dataset[st.session_state.color].unique()   
            
            if diff_colors.size > 1000:   # if more than 1000 unique colors, show error
                raise Exception("Too many unique values for the color variable. Change the color variable to a column with less unique values")        
            
            for col in diff_colors:        # one trace for each unique value of the color variable
                
                filtered_data = st.session_state.dataset[st.session_state.dataset[st.session_state.color] == col]       # filtered dataset by certain value of selected column
            
                grouped = filtered_data.groupby(st.session_state.x_axis)      # group by same value, get dictionary with key and group
                x_values = grouped.size().index     # unique x values 
                y_values = grouped.size().values    # count of each x value

                # original indexes for each unique x value
                original_indices = [', '.join(map(str, group.index)) for _, group in grouped]
                
                # translate bar index to the samples it is containing
                st.session_state.translated_indexes.append(original_indices)

                fig.add_trace(go.Bar(x=x_values, 
                                        y=y_values,
                                        name=col if type(col) == str else str(col),
                                        #text=[f'Index: {i}<br>X: {x}<br>Color: {col}' for (i, x) in zip(original_indices, filtered_data[st.session_state.x_axis])],
                                        text=[f'Indexes: {idx}<br>X: {x}<br>Y: {y}<br>Color: {col}' for idx, x, y in zip(original_indices, x_values, y_values)],
                                        hoverinfo='text',                   # show only the text on hover
                                        textposition='none',                # hide text on the graph
                                        orientation='v',                    # vertical bars
                                        )
                              )

            custom_bargap=0.2
            
            fig.update_layout(title=dict(text=st.session_state.chart_title, x=0.5, xanchor='center', y=0.9, yanchor='top'), 
                                xaxis_title=dict(text=st.session_state.x_axis),
                                yaxis_title=dict(text="Ocurrences"),
                                dragmode="select", selectdirection="h",   # fits all height, just horizontal movement for selection
                                barmode=st.session_state.barmode_key,
                                bargap=custom_bargap,   # gap between bars
                                activeselection=dict(fillcolor='pink', opacity=0.001), showlegend=True)
                                
             
            if st.session_state.chart_toggle_color:   # if toggle is selected, show the colors
                # add color shapes
                for prev_sel in st.session_state.bar_chart_painting:   # newest appears in foreground layer
                    try:
                        fig.add_vrect(x0=prev_sel[0]-custom_bargap*0.075, x1=prev_sel[1]+custom_bargap*0.075,  
                                        annotation_text=prev_sel[2], annotation_position="top left", annotation_textangle=90,
                                        annotation_font_size=18, annotation_font_color="white", annotation_font_weight=600,
                                        line_width=0, fillcolor=prev_sel[3], opacity=1, layer="below")   # add colored rectangle for each label
                    except:   
                        fig.add_vrect(x0=prev_sel[0], x1=prev_sel[1],  
                                        annotation_text=prev_sel[2], annotation_position="top left", annotation_textangle=90,
                                        annotation_font_size=18, annotation_font_color="white", annotation_font_weight=600,
                                        line_width=0, fillcolor=prev_sel[3], opacity=1, layer="below")   # add colored rectangle for each label
    
    
            st.session_state.selected_data = st.plotly_chart(fig, key="data_selection_key", on_select="rerun", config=config)    # show and assign selection variable listening

            # debugging, see what this variables contain
            #st.write(st.session_state.selected_data.selection.points)   # selected bar (which contains samples)
            #st.write(st.session_state.translated_indexes)      # dict of dicts with enumerate of indexes inside each bar

            # LABELLING SECTION
            st.subheader("Labelling Section")
            # info about selected data samples
            try: 
                n_points=f"{len(st.session_state.selected_data.selection.points)}"
                txt = f"Diferent x-axis values selected:\t{n_points}"
                st.write(":white_check_mark: "+txt)
            except Exception:
                st.write(":question: No data samples selected on the graph...")
            
            # classes for labelling
            col1, col2, col3 = st.columns([1, 1, 1], vertical_alignment="bottom")
            with col2:  # add new class for label
                if st.text_input(":heavy_plus_sign: Add classes for the label:", value="", placeholder="New class for the label",
                            on_change=add_new_class_label, key="new_class_label_key"):
                    if st.session_state.new_class_label_key in st.session_state.label_classes:   # if didn't empty in before function
                        st.error("The class already exists... Please, add a new one", icon="🚨")
                    if not any(char.isalnum() for char in st.session_state.new_class_label_key):
                        st.error("The class name must contain at least one alphanumeric character", icon="🚨")
                    
            with col1:  # currently activated class
                st.multiselect(f":label: Activated class:", options=st.session_state.label_classes,
                                placeholder="Select the activated class",
                                max_selections=1, default=st.session_state.currently_selected_class, on_change= reload_currently_activated_class, key="currently_selected_class_key")
            
            with col3:
                st.button(":wastebasket: Delete classes options", on_click= delete_classes_options,
                          use_container_width=True, 
                          help="Delete from the activated class selector all the classes added before")    # delete all classes options


            _, col1, col2 = st.columns([0.22, 0.5, 1], vertical_alignment="bottom")
            with col1:
                st.session_state.color_picker = st.color_picker("Color:", value=st.session_state.color_picker,
                                on_change=reload_color_picker, key="color_picker_key",
                                help="Choose the color that will fill the next area selected on the graph")    # color picker for the activated class        
            with col2:
                st.toggle(":eye: Show the colors of the classes on the graph", value=st.session_state.chart_toggle_color, on_change=reload_chart_toggle_color,
                            help="Selecting this option will show the colors of the classes in the bar chart")    # toggle for showing colors in the bar chart
                
            if len(st.session_state.label_column) < 1:   # bug fix (error after resetting session state, when already labelled and change from edit Edit Data to Graphic Labelling)
                    st.session_state.label_column = [""]*st.session_state.dataset.shape[0]
                    
            # button to apply the class to the samples
            if st.session_state.currently_selected_class != [] and st.session_state.selected_data.selection.points != []:   # if at least one sample is selected and a class is activated   
                if st.button(f"Confirm preview of labelling for selected samples with activated class", on_click=label_selected_data_bar_chart,
                                type="primary", use_container_width=True):   # label selected data with activated class from label options
                    st.success("Showing preliminary labelling on the graph and in the table below", icon="✅")            
            else:    # disabled button, just to denote blockage
                st.button(f"Confirm preview of labelling for selected samples with activated class", disabled=True, type="primary",
                            use_container_width=True,
                            help="Only clickable if any data sample is selected and a class for the label is activated")   # label selected data with activated class from label options
        
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
            if st.button("Save labels", on_click= save_labels, type="primary", use_container_width=True):   # save changes: modify the dataset and show success message
                st.success("Labels saved successfully! Check the resulting dataset in Edit Data page", icon="✅")
                
        except Exception as e:
            #st.error(e)
            st.error("Please, select correct parameters to draw the bar chart... Problem: " + str(e), icon="🚨")    # if any error occurs, show message
           
           
    def reload_barmode_index() -> None:
        # reload the index of barmode
        st.session_state.barmode_index = ["group", "stack", "overlay"].index(st.session_state.barmode_key)
    
    def label_selected_data_bar_chart() -> None:
        # label the selected data with the activated class and add color shape to plot in bar chart
        for point in st.session_state.selected_data.selection.points:       # a point is equal to a bar
            current_curve = st.session_state.translated_indexes[point["curve_number"]]     # get the class of the bar
            idx_to_label = current_curve[point["point_index"]]       # string with all indexes to label
            for idx in [int(x) for x in idx_to_label.split(', ')]:   # iterate over all indexes in mixed in the bar
                st.session_state.label_column[idx] = st.session_state.currently_selected_class[0]
        #add info for colored rectangle to plot next time
        st.session_state.bar_chart_painting.append([min(point['x'] for point in st.session_state.selected_data.selection.points),       # x0
                                                    max(point['x'] for point in st.session_state.selected_data.selection.points),       # x1
                                                    st.session_state.currently_selected_class[0],      # class
                                                    st.session_state.color_picker])                    # color
            

    #...................PIE PLOT..............................................        
    def pie_chart() -> None:
        st.write(":construction: Pie Chart not supported yet...") 
    
    
    
    
            
    #---------------------------- PAGE ------------------------------#
    if st.session_state.dataset is not None:   # if any data was uploaded

        # configuration for all plotly charts
        config = {'displayModeBar': True,
                'toImageButtonOptions': {
                        'format': 'png', # one of png, svg, jpeg, webp
                        'filename': st.session_state.file_name+'_plot',
                        'height': 1080,
                        'width': 1920,
                        'scale': 5 # Multiply title/legend/axis/canvas sizes by this factor
                        }
                }

        st.header("Graphic Labelling")
        st.subheader(f"File name: {st.session_state.file_name}")
        
        graph_options = ["None", "Line Chart", "Scatter Plot", "Bar Chart"] #, "Pie Chart"]   # all the graph types available
        st.selectbox("Graph type", graph_options, index = st.session_state.graph_selectbox_index,
                        on_change=reload_graph_type_selectbox, key="graph_type",    # select the graph type (index is preselected option)
                        help="When changed, all the session state variables will be reset to default values")
        
        if st.session_state.graph_type == "None":     # nothing
            st.info("Select a graph type to show all its parameters and display the data", icon=":material/help_center:")
        with st.container(border = True):
            if st.session_state.graph_type == "Line Chart":
                line_chart()
            elif st.session_state.graph_type == "Scatter Plot":
                scatter_plot()
            elif st.session_state.graph_type == "Bar Chart":
                bar_chart()
                
            '''elif st.session_state.graph_type == "Pie Chart":    
                pie_chart()'''

    else:
        st.info("Please, upload a file first", icon=":material/help_center:")    # if no file uploaded, show info message