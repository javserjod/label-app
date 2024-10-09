import streamlit as st
import pandas as pd
import io    # just for conversion to Excel (also downloaded module xlsxwriter)

# import resetting for every session state variable in plot in graphic labelling
from reset_functions import reset_all_session_state

def app():
    
    #-------------------------- FUNCTIONS ---------------------------#
    def reload_data_editor() -> None:
        # reloads the data editor to update the dataset (rebuild some logic on it)
        
        # if row deleted (can be one or more row at once)
        if len(st.session_state.data_editor_key["deleted_rows"]) > 0:
            try:
                for del_row in st.session_state.data_editor_key["deleted_rows"]:
                    st.session_state.dataset.drop(del_row, inplace=True)
                del_row_str = ', '.join(map(str, st.session_state.data_editor_key["deleted_rows"]))   # convert to string to show in the message
                if len(st.session_state.data_editor_key["deleted_rows"]) == 1:    # just one, singular text
                    st.success("Row ["+ del_row_str +"] deleted successfully. Indexes reset", icon="✅")
                else:      # more than one, plural text
                    st.success("Rows ["+ del_row_str +"] deleted successfully. Indexes reset", icon="✅")
                st.session_state.data_editor_key["deleted_rows"] = []   # reset the deleted rows list
                st.session_state.dataset.reset_index(drop=True, inplace=True)   # reset the index of the dataset, so it starts from 0 and goes up consecutive numbers
            except Exception as e:
                st.error("Error while deleting rows: "+str(e), icon="🚨") 
        
        # if row added (only one row at a time) -> empty rows will contain empty strings instead of original None
        if len(st.session_state.data_editor_key["added_rows"]) > 0:
            try:
                new_row = pd.DataFrame([[""] * len(st.session_state.dataset.columns)], columns=st.session_state.dataset.columns)   # create a new empty row with the same columns as the dataset
                st.session_state.dataset = pd.concat([st.session_state.dataset, new_row], ignore_index=True)   # add a new empty row at the end of the dataset, already correct index

                st.success("New empty row added at last index successfully", icon="✅")
                st.session_state.data_editor_key["added_rows"] = []   # reset the added rows list  
            except Exception as e:
                st.error("Error while adding new row: "+str(e), icon="🚨") 
             
        # if row cell edited (only one cell at a time) -> 
        if len(st.session_state.data_editor_key["edited_rows"]) > 0:
            try:
                key_row = list(st.session_state.data_editor_key["edited_rows"].keys())[0]   # get key of the first and only dictionary = index of the row
                key_col = list(st.session_state.data_editor_key["edited_rows"][key_row].keys())[0]      # get the only key of the inside dictionary = column name
                val_new = list(st.session_state.data_editor_key["edited_rows"][key_row].values())[0]    # get the only value of the inside dictionary = new value
                if val_new == None:   # if the value is None, replace with an empty string
                    val_new = ""
                    
                if val_new == "" and st.session_state.dataset.dtypes[key_col] != "object":   # empty strings only available in object columns. Otherwise, error, don't allow
                    # None value will be on the cell to avoid error and alert the user about it
                    st.session_state.dataset.at[key_row, key_col] = None   # cahnge value for None
                    raise ValueError(f"cannot convert value \"{val_new}\" to the type of the column, {st.session_state.dataset.dtypes[key_col]}. Replacing with None. Please, correct it before continuing...")
                else:
                    val_new_conv = pd.Series([val_new]).astype(st.session_state.dataset.dtypes[key_col]).iloc[0]      # try to convert to variable data type
                    st.session_state.dataset.at[key_row, key_col] = val_new_conv   # execute the change of value in the dataset
                    if val_new_conv != "":
                        st.success("Row ["+str(key_row)+"], Column ["+str(key_col)+"] edited successfully. New value: ["+str(val_new_conv)+"]", icon="✅")
                    else:   # just indicate that the value was changed from None to empty string for compatibility reasons
                        st.success("Row ["+str(key_row)+"], Column ["+str(key_col)+"] edited successfully. New value: ["+str(val_new_conv)+"], forced change from None to empty string", icon="✅")
                    st.session_state.data_editor_key["edited_rows"] = []   # reset the edited cells list  
            
            except Exception as e:
                st.error("Error while editing cell: "+str(e), icon="🚨") 
                
            
    def get_current_headers() -> list:
        # returns list with the current headers of the current dataset being edited
        return st.session_state.dataset.columns.tolist()
    
    def save_filtered_dataset() -> None:
        # save the filtered dataset in the session state variable. Used on_click inside Conditional Filtering expander
        st.session_state.dataset = st.session_state.filtered_dataset         # dataset var points to the filtered one, O(1)
        #st.session_state.dataset = st.session_state.filtered_dataset.copy()   # direct assigment is faster than copy O(n)
        st.session_state.filtered_dataset = None       # this variable is now pointing to None. Only dataset is pointing to the filtered dataset
        st.success("Conditional filtering applied successfully. Dataset updated", icon="✅")
 
    #---------------------------- PAGE ------------------------------#
    if st.session_state.dataset is not None:   # if any data was uploaded
        
        st.header("Edit Data")
        st.subheader(f"File name: {st.session_state.file_name}")
        
        st.data_editor(st.session_state.dataset,
                        use_container_width = True,  
                        hide_index = False,        # show the index column
                        num_rows = "dynamic",      # dynamic -> no indexes but allows adding rows with a click and deleting selected rows
                        on_change=reload_data_editor,   # to reload when edited cells, or added or deleted rows
                        key="data_editor_key")     # key contains only modifications to the dataset
        
        # metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            delta_rows = st.session_state.dataset.shape[0] - st.session_state.original_dataset.shape[0]   # difference in number of rows regarding the original dataset
            st.metric("Number of rows", value=st.session_state.dataset.shape[0],
                      delta=delta_rows if delta_rows != 0 else None)
        
        with col2:
            delta_cols = st.session_state.dataset.shape[1] - st.session_state.original_dataset.shape[1]   # difference in number of columns regarding the original dataset
            st.metric("Number of columns", value=st.session_state.dataset.shape[1],
                      delta=delta_cols if delta_cols != 0 else None)
        with col3:
            original_memory_usage=st.session_state.original_dataset.memory_usage(deep=True).sum()   # sum of memory usage of each column = total (BYTES)
            current_memory_usage=st.session_state.dataset.memory_usage(deep=True).sum()
            diff_memory_usage = current_memory_usage - original_memory_usage
            size_in_kb = f"{current_memory_usage/(1024):.2f}"
            size_in_mb = f"{current_memory_usage/(1024**2):.2f}"
            if float(size_in_mb) > 1:   # use MB
                st.metric("Size of dataset in memory", value=size_in_mb+" MB",
                        delta=f"{(diff_memory_usage)/(1024**2):.2f}" if diff_memory_usage != 0 else None,
                        help="Size in memory after loading the file, which may differ from the actual file size due to Pandas conversion") 
            else:    # use kB
                st.metric("Size of dataset in memory", value=size_in_kb+" kB",
                        delta=f"{(diff_memory_usage)/(1024):.2f}" if diff_memory_usage != 0 else None,
                        help="Size in memory after loading the file, which may differ from the actual file size due to Pandas conversion")
                
        
        st.markdown("######")   # add space between the metrics and the description
        
        
        # HANDLE NA VALUES (DROP AND FILL)
        with st.expander("Handle NA values"):
            na_table = pd.DataFrame(st.session_state.dataset.isna().sum(), columns=["NA Count per column"]) # count the number of NA values per column
            columns_with_na = na_table[na_table.iloc[:, 0] > 0].index.values   # get the columns with NA values
            if len(columns_with_na) > 0:   # if any column has NA values, this functionality will be available
                with st.form("handle_na_form"):
                    col1, col2 = st.columns([1, 1], vertical_alignment="center")
                    with col1:
                        # show the number of NA values per column (NaN and None)
                        st.dataframe(na_table, use_container_width=True)   # show the number of NA values per column
                    with col2:
                        if st.form_submit_button("Delete all rows with any NA value", use_container_width=True):
                            st.session_state.dataset = st.session_state.dataset.dropna()
                            reset_all_session_state()   # reset all charts and labelling variables from session state to default value
                            st.rerun()   # rerun the app to update the table
                            
                        if st.form_submit_button("Delete all columns with any NA value", use_container_width=True):
                            st.session_state.dataset = st.session_state.dataset.dropna(axis=1)
                            reset_all_session_state()   # reset all charts and labelling variables from session state to default value
                            st.rerun()   # rerun the app to update the table
                    
                    col3, col4, col5= st.columns([1, 1, 1])
                    with col3:
                        st.metric("Rows with NA: ", value=st.session_state.dataset.isna().any(axis=1).sum())  # count the number of rows with any NA value
                    with col4:
                        st.metric("Columns with NA: ", value=len(columns_with_na))
                    with col5:
                        st.metric("Total NA values: ", value=st.session_state.dataset.isna().sum().sum())
                            
                    st.multiselect("Select one or more columns to fill NA values with chosen values:", options= columns_with_na, 
                                placeholder="Choose one or more columns", default=None, key="columns_to_fill_na",
                                help="Select one or more columns that will be filled with the chosen value at any cell with NA value")
                    
                    st.text_input("Write the filler value:", placeholder="Filler value",
                                key="filler_value", value="", help="By default, it will be an empty string")
                    
                    if st.form_submit_button("Fill NA values with chosen value"):
                        if len(st.session_state.columns_to_fill_na) > 0:
                            try:
                                for col in st.session_state.columns_to_fill_na:   # just for checking if an error will be raised during type converison, so nothing is changed yet
                                    try:
                                        filler_value_conv = pd.Series([st.session_state.filler_value]).astype(st.session_state.dataset.dtypes[col]).iloc[0]
                                    except:
                                        raise ValueError(f"Filler value \"{st.session_state.filler_value}\" is not compatible with the type of the column \"{col}\", {st.session_state.dataset.dtypes[col]}")
                                
                                for col in st.session_state.columns_to_fill_na:   # actual filling of NA values
                                    filler_value_conv = pd.Series([st.session_state.filler_value]).astype(st.session_state.dataset.dtypes[col]).iloc[0]
                                    st.session_state.dataset[col].fillna(value=filler_value_conv, inplace=True)
                                
                                # if everything went well
                                reset_all_session_state()   # reset all charts and labelling variables from session state to default value
                                st.rerun()   # rerun the app to update the table
                            except Exception as e:
                                st.error("Error while filling NA values ---- " + str(e), icon="🚨")
                        else:
                            st.error("No column was selected to fill NA values. Please, select one to proceed.", icon="🚨")
            else:
                st.info("No NA values in the dataset", icon="✅")
        
        
        # MODIFY HEADERS
        with st.expander("Modify headers"):
            if len(st.session_state.dataset.columns) > 0:   # only available if there are columns in the dataset
                with st.form("header_form"):
                    st.write("Write the new headers' names for the dataset:")  
                    
                    written_headers = [None] * len(st.session_state.dataset.columns)   # variable to store text_input values
                    for i in range(0, len(st.session_state.dataset.columns)):
                        written_headers[i] = st.text_input(f"Header {i}", value = st.session_state.dataset.columns[i])    # stored as strings
                        
                    new_headers = st.toggle("Move down current headers and insert the new ones?",
                                            help = "Selecting this option will insert the current headers as the first row, and create new headers with the values given. Not selecting this option will just rename the current headers with the indicated values.")  
                    
                    if st.form_submit_button("Submit changes"):
                        try:    
                            if new_headers:    # move down current headers and insert the new ones  
                                # do type conversion from existing reference row
                                current_headers = get_current_headers()                 # get the current headers
                                try:
                                    for i, col in enumerate(current_headers):
                                        current_headers[i] = pd.Series([col]).astype(st.session_state.dataset.dtypes[col]).iloc[0]      # convert columns names to their type and add to the list
                                        # add correctly False boolean values
                                        if st.session_state.dataset.dtypes[col] == 'bool':   
                                            if col.strip().lower() == "false" or col == "0":
                                                current_headers[i] = False    
                                except:
                                    raise ValueError(f"Cannot convert column name \"{col}\" to the type it contains, {st.session_state.dataset.dtypes[col]}")
                                
                                '''if len(st.session_state.dataset.values) > 0:                        # conversion only if there's at least one existing row (needed to have a reference for the types)
                                    for i in range(len(st.session_state.dataset.columns)):          # iterate over the previous headers to force type conversion
                                        if type(current_headers[i]) != str:                         # conversion only if not string
                                            current_headers[i] = type(st.session_state.dataset.values[0][i])(current_headers[i])   # force the type conversion if not string
                                '''
                                st.session_state.dataset = st.session_state.dataset.set_axis(written_headers, axis="columns")    # change the headers to the written ones
                                st.session_state.dataset = pd.concat([pd.DataFrame([current_headers], columns=written_headers), 
                                                                        st.session_state.dataset], ignore_index=True)     # join previous headers as first row, resulting in one dataset with default headers
                                st.session_state.dataset.reset_index(drop=True, inplace=True)   # reset the index of the dataset, so it starts from 0 and goes up consecutive numbers
                                #st.success("Previous headers are now the first row and new headers were added successfully", icon="✅")   # on top of screen
                                reset_all_session_state()   # reset all variables from session state to default value
                                st.rerun()   # rerun the app to update the table
                                
                            else:   # just rename the headers
                                if written_headers==get_current_headers():   # if the headers are the same, do nothing
                                    st.warning("No changes were made to the headers...", icon="❓")
                                else:
                                    st.session_state.dataset.columns = written_headers
                                    #st.success("Renaming of headers was successful", icon="✅")
                                    reset_all_session_state()   # reset all variables from session state to default value
                                    st.rerun()   # rerun the app to update the table
                        except Exception as e:
                            st.error("Error while modifying the headers ---- " + str(e), icon="🚨")
            else:
                st.error("No headers to modify. Please, add some columns to the dataset first with the 'Add variable column functionality'", icon="🚨")
        
        
        # ADDITION OF VARIABLE         
        with st.expander("Add variable column"):
            with st.form("add_column_form"):
                col1, col2 = st.columns([1, 1])
                with col1:
                    st.text_input("Write the name of the variable to add:", placeholder="Write the name of the new variable",
                                key="column_to_add", help="Write the name of the new column to add to the dataset. Can't be repeated nor empty")
                with col2:    
                    #st.text_input("Column index where variable is added:", placeholder="Insertion index", value = st.session_state.dataset.shape[1],
                    #            key="column_add_index", help="Write the index where the new column will be inserted. If left empty, it will be added at the end of the dataset. Index must be in the intervbal [0, number of columns]") 
                    st.slider("Column index where variable is added:", 
                            min_value=0, max_value=max(1, st.session_state.dataset.shape[1]), # in case the dataset is empty, set the max value to 1
                            value=max(1, st.session_state.dataset.shape[1]), key="column_add_index",
                            help="Write the index where the new column will be inserted. If left empty, it will be added at the end of the dataset. Index must be in the intervbal [0, number of columns]")
                
                dtypes_options = ["object", "int64", "float64", "bool", "datetime64"]
                col1, col2 = st.columns([1, 1])
                with col1:
                    st.text_input("Default value of the new column:", placeholder="Insert the default value", value = "",
                                key="column_add_value", help="Write the default value for the new column. By default, it will be an empty string and try to convert to the dtype selected")     
                with col2:    
                    st.selectbox("Select the Pandas dtype of the new column:", options=dtypes_options, index=0,
                                 placeholder="Choose the Pandas dtype of the new column", key="column_add_dtype",
                                 help="Select the Pandas dtype of the new column. By default, it will be dtype object")
                
                try:
                    if st.form_submit_button("Confirm addition of new column"):
                        if st.session_state.column_to_add != "":   # if any name was written
                            if st.session_state.column_to_add not in get_current_headers():   # if the name is not repeated
                                try:
                                    
                                    st.session_state.dataset.insert(loc=int(st.session_state.column_add_index),
                                                                column=st.session_state.column_to_add.strip(),
                                                                value=pd.Series([st.session_state.column_add_value]*st.session_state.dataset.shape[0], dtype=st.session_state.column_add_dtype),
                                                                allow_duplicates=False)   # drop the selected column
                                    
                                    # add correctly False boolean values -> pd.Series doesn't operate good with false/0, and changes it for true/1 without permission
                                    if st.session_state.column_add_dtype == 'bool':   
                                        if st.session_state.column_add_value.strip().lower() == "false" or st.session_state.column_add_value == "0":
                                            st.session_state.dataset[st.session_state.column_to_add.strip()].replace({True:False}, inplace=True)

                                    # if everything went well
                                    reset_all_session_state()   # reset all charts and labelling variables from session state to default value
                                    st.rerun()   # rerun the app to update the table
                                
                                except Exception as e:   # delete the just added column if error (if it was added)
                                    try:
                                        st.session_state.dataset = st.session_state.dataset.drop(st.session_state.column_to_add, axis=1)    # delete the just added column
                                    except:
                                        pass
                                    raise ValueError(f"Check if the default value is compatible with the dtype selected")
                            else:
                                st.error("The name of the new column is already in use. Please, write a different one to proceed", icon="🚨")
                        else:
                            st.error("No name assigned to the new column. Please, write one to proceed", icon="🚨")
                except Exception as e:
                    st.error("Error while adding the new column ---- " + str(e), icon="🚨")
                    
                    
        # DELETION OF VARIABLE         
        with st.expander("Delete variable column"):
            if len(st.session_state.dataset.columns) > 0:   # only available if there are columns in the dataset
                with st.form("delete_column_form"):
                    st.selectbox("Select the column to delete:", options=get_current_headers(),
                                index=None, placeholder="Choose a variable",
                                key="column_to_delete") 
                    
                    if st.form_submit_button("Confirm deletion of selected column"):
                        if st.session_state.column_to_delete is not None:
                            st.session_state.dataset = st.session_state.dataset.drop(st.session_state.column_to_delete, axis=1)   # drop the selected column
                            if st.session_state.dataset.columns.tolist() == []:   # if no columns left, reset the dataset to empty
                                st.session_state.dataset = st.session_state.dataset[0:0]   # empty dataset
                            # if everything went well
                            reset_all_session_state()   # reset all charts and labelling variables from session state to default value
                            st.rerun()   # rerun the app to update the table
                            #st.success("Column "+st.session_state.column_to_delete+" was deleted successfully", icon="✅")   # on top of screen
                        else:
                            st.error("No column was selected to delete. Please, select one to proceed.", icon="🚨")
            else:
                st.error("No columns to delete. Please, add some columns to the dataset first with the 'Add variable column functionality'", icon="🚨")
        
        
        # REPLACEMENT OF VALUES
        with st.expander("Replace values"):
            if st.session_state.dataset.shape[0] > 0:   # only available if there are rows in the dataset
                with st.form("replace_values_form"):
                    
                    # text inputs for the value to be replaced and the replacement value
                    col1, col2 = st.columns(2)
                    with col1:
                        st.text_input("Write the value to be replaced:", placeholder="Value to be replaced",
                                    key="value_replaced", value="", help="By default, it will be an empty string")   
                    with col2:
                        st.text_input("Write the replacement value:", placeholder="Replacement value",
                                key="replacement_value", value="", help="By default, it will be an empty string")
                    
                    # multiselect for the columns where the replacement will be applied
                    st.multiselect("Select the columns to apply the replacement:", options=get_current_headers(),
                                default=None, key="columns_where_replace", placeholder="Columns where replacement will be applied",
                                help="Select one or more columns to apply the replacement")
                    
                    if st.form_submit_button("Confirm replacement"):
                        if len(st.session_state.columns_where_replace) > 0:    # any column where replace
                            try:
                                for col in st.session_state.columns_where_replace:
                                    # replacement. Make a conversion to the type of the column
                                    try:
                                        val_replaced_conv = pd.Series([st.session_state.value_replaced]).astype(st.session_state.dataset.dtypes[col]).iloc[0]
                                        # add correctly False boolean values
                                        if st.session_state.dataset.dtypes[col] == 'bool':   
                                            if st.session_state.value_replaced.strip().lower() == "false" or st.session_state.value_replaced == "0":
                                                val_replaced_conv = False
                                    except:
                                        raise ValueError(f"Replaced value \"{st.session_state.value_replaced}\" can't be in column \"{col}\" because it's not compatible with its type {st.session_state.dataset.dtypes[col]}")
                                    try:
                                        replacement_val_conv = pd.Series([st.session_state.replacement_value]).astype(st.session_state.dataset.dtypes[col]).iloc[0]
                                        # add correctly False boolean values
                                        if st.session_state.dataset.dtypes[col] == 'bool':   
                                            if st.session_state.replacement_value.strip().lower() == "false" or st.session_state.replacement_value == "0":
                                                replacement_val_conv = False
                                    except:
                                        raise ValueError(f"Replacement value \"{st.session_state.value_replaced}\" is not compatible with the type of the column \"{col}\", {st.session_state.dataset.dtypes[col]}")
                                    
                                    st.session_state.dataset[col] = st.session_state.dataset[col].replace(val_replaced_conv, replacement_val_conv)   # replace the values                                                
                                # if everything went well
                                reset_all_session_state()   # reset all charts and labelling variables from session state to default value
                                st.rerun()   # rerun the app to update the table
                            except Exception as e:
                                st.error("Error while replacing the values ---- " + str(e), icon="🚨")
                        
                        else:
                            st.error("No column was selected to perform the replacement", icon="🚨")
            else:
                st.error("No cells to replace values. Please, add some rows to the dataset first with the 'Insert new sample at chosen index' functionality or by clicking on the table directly. Columns are needed too, in case there isn't anyone, add one with 'Add variable column'", icon="🚨")
        

        # INSERTION OF NEW SAMPLE
        with st.expander("Insert new sample at chosen index"):
            with st.form("insert_new_sample_form"):
                st.write("Write values compatible with the column type. Empty strings only available in object columns.")
                try:
                    for var in get_current_headers():
                        st.text_input(var, key=var, placeholder=st.session_state.dataset.dtypes[var])
                except:
                    pass    # a bug sometimes happens here, when adding label column and making a repalcement in it, 
                            #text input related to label column produces an error, which can be ignored by changing pages...
                            # but it's better to hide it with this try-except block
                
                st.slider("Choose the index to insert the new sample:", 
                          min_value=0, max_value=max(1, st.session_state.dataset.shape[0]), # in case the dataset is empty, set the max value to 1
                          value=0, key="slider_index_key", format= "Index %i",
                          help="Select the index where the new sample will be inserted. Choosing 0 creates the sample at the beginning of the dataset")
                
                if st.form_submit_button("Insert the new sample"):
                    try:
                        new_sample_values = []   # list to store the values of the new sample after conversion (session state keys used before can't be changed)
                        try:
                            for var in get_current_headers():
                                new_sample_values.append(pd.Series([st.session_state[var]]).astype(st.session_state.dataset.dtypes[var]).iloc[0])   # convert the value to the type of the column
                                
                                # add correctly False boolean values
                                if st.session_state.dataset.dtypes[var] == 'bool':   
                                    if st.session_state[var].strip().lower() == "false" or st.session_state[var] == "0":
                                        new_sample_values[-1] = False    # change last value for false
                        
                        except:      # error while converting the value to the type of the column
                            raise ValueError(f"Cannot convert value \"{st.session_state[var]}\" to the type of the column \"{var}\", {st.session_state.dataset.dtypes[var]}")
                            
                        new_sample = pd.DataFrame([new_sample_values], columns=get_current_headers())   # create a new row with the values given
                        st.session_state.dataset = pd.concat([st.session_state.dataset.iloc[:st.session_state.slider_index_key], 
                                                              new_sample, 
                                                              st.session_state.dataset.iloc[st.session_state.slider_index_key:]], ignore_index=True)   # insert the new sample at the selected index, reset indexes
                        # if everything went well
                        reset_all_session_state()   # reset all charts and labelling variables from session state to default value
                        st.rerun()   # rerun the app to update the table
                    
                    except Exception as e:
                        st.error("Error while inserting the new sample ---- " + str(e), icon="🚨")
        
        
        # CONDITIONAL FILTERING                
        with st.expander("Conditional filtering"):
            if st.session_state.dataset.shape[0] > 0 and st.session_state.dataset.shape[1] > 0:   # only available if there are rows and columns in the dataset
                with st.form("conditional_filtering_form"):
                    st.write("Keep the samples that meet the condition in the selected column according to the comparison operator and value given.")
                    st.selectbox("Select the column to apply the condition:", options=get_current_headers(),
                                index=None, placeholder="Choose a variable",
                                key="column_to_filter")
                    st.multiselect("Select the operator to apply:", options=["==", "!=", ">", "<", ">=", "<="],
                                default=None, key="condition_to_apply", placeholder="Choose one comparison operator",
                                help="Select one comparison operator to apply to the selected column")
                    st.text_input("Write the value to compare:", placeholder="Value to compare",
                                key="value_to_compare", value="", 
                                help="Write the value to compare with filter the column using the logic operator")
                        
                    if st.form_submit_button("Simulate the filtering and preview the changes", help="This will not apply the changes to the dataset yet. A new button will appear, which is the one that will apply the changes."):   # simulate the filtering
                        try:
                            if st.session_state.column_to_filter != None and len(st.session_state.condition_to_apply) > 0:
                                if st.session_state.dataset.dtypes[st.session_state.column_to_filter] == "object":   # accept any value to compare, whatever type it is
                                    # no manual conversion needed
                                    # use backticks around column name (mandatory if contains spaces, punctuations, starting with digits...). Value to compare (already string) around double quotes
                                    query_str = f"`{st.session_state.column_to_filter}` {st.session_state.condition_to_apply[0]} \"{st.session_state.value_to_compare}\""
                                    try:  # directly make the query
                                        st.session_state.filtered_dataset = st.session_state.dataset.query(query_str)   # filter the dataset  
                                    except:   # error while filtering
                                        raise ValueError(f"Something went wrong with the query: `{st.session_state.column_to_filter}` {st.session_state.condition_to_apply[0]} \"{st.session_state.value_to_compare}\"")
                                
                                else:   # data type is not object (empty string as value not allowed)
                                    if st.session_state.value_to_compare == "":   # if left empty, indicate the error (this is optional, because an exception would be raised anyway)
                                        raise ValueError("Value to compare cannot be empty if type is not object")
                                    else:   # not empty string, now try conversions
                                        try:
                                            value_to_compare_conv = pd.Series([st.session_state.value_to_compare]).astype(st.session_state.dataset.dtypes[st.session_state.column_to_filter]).iloc[0]   # convert the value to the type of the column
                                            # add correctly False boolean values
                                            if st.session_state.dataset.dtypes[st.session_state.column_to_filter] == 'bool':   
                                                if st.session_state.value_to_compare.strip().lower() == "false" or st.session_state.value_to_compare == "0":
                                                    value_to_compare_conv = False    
                                            
                                            # use backticks around column name (mandatory if contains spaces, punctuations, starting with digits...)
                                            query_str = f"`{st.session_state.column_to_filter}` {st.session_state.condition_to_apply[0]} {value_to_compare_conv}"   # create the query string
                                            try:   # make the query
                                                st.session_state.filtered_dataset = st.session_state.dataset.query(query_str)   # filter the dataset   
                                                st.session_state.filtered_dataset.reset_index(drop=True, inplace=True)   # reset the index of the dataset, so it starts from 0 and goes up consecutive numbers   
                                            except:   # error while filtering
                                                raise ValueError(f"Something went wrong with the query: {query_str}")

                                        except:    # error while converting
                                            raise ValueError(f"Cannot convert value \"{st.session_state.value_to_compare}\" to the type of the column \"{st.session_state.column_to_filter}\", {st.session_state.dataset.dtypes[st.session_state.column_to_filter]}")
                                
                                st.dataframe(st.session_state.filtered_dataset, use_container_width=True)   # preview of the changes
                                
                                # metrics for the future filtered dataset, comparing with the current dataset
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    delta_rows_filter = st.session_state.filtered_dataset.shape[0] - st.session_state.dataset.shape[0]   # difference in number of rows regarding the current dataset
                                    st.metric("Number of rows after filtering", value=st.session_state.filtered_dataset.shape[0],
                                                delta=delta_rows_filter if delta_rows_filter != 0 else None,
                                                help="Difference respect to the current dataset, not the original one")
                                with col2:     # this won't change, but we add it for consistency
                                    delta_cols_filter = st.session_state.filtered_dataset.shape[1] - st.session_state.dataset.shape[1]   # difference in number of columns regarding the current dataset
                                    st.metric("Number of columns after filtering", value=st.session_state.filtered_dataset.shape[1],
                                                delta=delta_cols_filter if delta_cols_filter != 0 else None,
                                                help="Difference respect to the current dataset, not the original one")
                                with col3:
                                    original_memory_usage_filter=st.session_state.dataset.memory_usage(deep=True).sum()   # sum of memory usage of each column = total (BYTES)
                                    current_memory_usage_filter=st.session_state.filtered_dataset.memory_usage(deep=True).sum()
                                    diff_memory_usage_filter = current_memory_usage_filter - original_memory_usage_filter
                                    size_in_kb_filter = f"{current_memory_usage_filter/(1024):.2f}"
                                    size_in_mb_filter = f"{current_memory_usage_filter/(1024**2):.2f}"
                                    if float(size_in_mb_filter) > 1:   # use MB
                                        st.metric("Size of filtered dataset in memory", value=size_in_mb_filter+" MB",
                                                delta=f"{(diff_memory_usage_filter)/(1024**2):.2f}" if diff_memory_usage_filter != 0 else None,
                                                help="Size in memory after filtering the dataset, which may differ from the actual file size due to Pandas conversion. Difference respect to the current dataset, not the original one") 
                                    else:    # use kB
                                        st.metric("Size of filtered dataset in memory", value=size_in_kb_filter+" kB",
                                                delta=f"{(diff_memory_usage_filter)/(1024):.2f}" if diff_memory_usage_filter != 0 else None,
                                                help="Size in memory after filtering the dataset, which may differ from the actual file size due to Pandas conversion. Difference respect to the current dataset, not the original one")
                                
                                # second button to apply the changes
                                if st.form_submit_button("Apply changes to dataset", 
                                                        help=":warning: This will remove the rest of the samples",
                                                        on_click=save_filtered_dataset):   # save in the state session variable the filtering made
                                    # update the dataset with the filtered one
                                    reset_all_session_state()   # reset all charts and labelling variables from session state to default value
                                    st.rerun()   # rerun the app to update the table   
            
                            else:
                                raise ValueError("No column or condition was selected to perform the filtering")
                            
                        except Exception as e:   # catch any error raised
                            st.error("Error while filtering the dataset ---- " + str(e), icon="🚨")
            else:
                st.error("Can't use this functionality. At least one row and one column are needed in the dataset", icon="🚨")
    
    
        # DOWNLOAD DATASET SECTION-------------------------------------
        st.divider()
        st.subheader("Download modified dataset")
        
        @st.cache_data
        def convert_df_csv(df) -> str:
            # converts the dataframe to a csv file
            # IMPORTANT: Cache the conversion to prevent computation on every rerun
            return df.to_csv(index=False).encode("utf-8")
                             
        @st.cache_data
        def convert_df_json(df) -> str:
            # converts the dataframe to a json file
            # IMPORTANT: Cache the conversion to prevent computation on every rerun
            return df.to_json(orient="records")   # each row is a dictionary, list of dictionaries
         
        @st.cache_data
        def convert_df_parquet(df) -> str:
            # converts the dataframe to a parquet file
            # IMPORTANT: Cache the conversion to prevent computation on every rerun
            return df.to_parquet()
        
        @st.cache_data
        def convert_df_excel(df) -> str:
            # converts the dataframe to a xlsx file
            # IMPORTANT: Cache the conversion to prevent computation on every rerun
            output = io.BytesIO()
            writer = pd.ExcelWriter(output, engine="xlsxwriter", mode="w")    # download module xlsxwriter
            df.to_excel(writer, index=False, sheet_name="sheet1")   # sheet1 is default name of the sheet
            writer.close()
            return output.getvalue()    # return the string with the file
            
        def reload_download_file_name() -> None:
            # reloads the download file name when changed
            st.session_state.download_file_name = st.session_state.download_file_name_key.strip()  # remove leading and trailing whitespaces
       
        # default name was assigned when uploading dataset
        st.text_input("Name for the downloaded file:", value=st.session_state.download_file_name,
                        key="download_file_name_key", on_change=reload_download_file_name,
                        help="Write the name of the file to be downloaded. The extension will be added automatically if not present, when clicking the download button. Please, in order to save correctly the written name, press Enter key or click anywhere but directly on the download button...")
            
        st.write("Current selected name: " + st.session_state.download_file_name)   # show the name of the file
        
        if len(st.session_state.download_file_name_key) > 1 and st.session_state.download_file_name_key not in [".csv", ".json", ".parquet", ".xlsx"]:   # if the name is not empty (and not empty after removing the extension)
            success_download_format = ""
            
            col1, col2 = st.columns(2)
            with col1:
                # CSV download button
                try:
                    if st.download_button(label=":material/download: Download modified dataset as CSV", data=convert_df_csv(st.session_state.dataset),
                                        file_name = st.session_state.download_file_name if st.session_state.download_file_name.endswith('.csv') else st.session_state.download_file_name+'.csv', 
                                        mime="text/csv", type="primary",
                                        use_container_width=True): 
                        #st.success(f"Dataset downloaded successfully in format CSV - {st.session_state.download_file_name if st.session_state.download_file_name.endswith('.csv') else st.session_state.download_file_name+'.csv'}", icon="✅")
                        success_download_format = "CSV"
                except Exception as e:
                    st.error(str(e), icon="🚨")
            
            with col2:    
                # JSON download button
                try:
                    if st.download_button(label=":material/download: Download modified dataset as JSON", data=convert_df_json(st.session_state.dataset),
                                        file_name = st.session_state.download_file_name if st.session_state.download_file_name.endswith('.json') else st.session_state.download_file_name+'.json', 
                                        mime="text/json", type="primary",
                                        use_container_width=True): 
                        #st.success(f"Dataset downloaded successfully in format JSON as {st.session_state.download_file_name if st.session_state.download_file_name.endswith('.json') else st.session_state.download_file_name+'.json'}", icon="✅")
                        success_download_format = "JSON"
                except Exception as e:
                    st.error(str(e), icon="🚨")
            
            col1, col2 = st.columns(2)
            with col1:    
                # Parquet download button
                try:
                    if st.download_button(label=":material/download: Download modified dataset as Parquet", data=convert_df_parquet(st.session_state.dataset),
                                        file_name = st.session_state.download_file_name if st.session_state.download_file_name.endswith('.parquet') else st.session_state.download_file_name+'.parquet', 
                                        mime="text/parquet", type="primary",
                                        use_container_width=True): 
                        #st.success(f"Dataset downloaded successfully in format Parquet as {st.session_state.download_file_name if st.session_state.download_file_name.endswith('.parquet') else st.session_state.download_file_name+'.parquet'}", icon="✅")
                        success_download_format = "Parquet"
                except Exception as e:
                    st.error(str(e), icon="🚨")
            
            with col2:
                # Excel XLSX download button
                try:
                    if st.download_button(label=":material/download: Download modified dataset as XLSX", data=convert_df_excel(st.session_state.dataset),
                                        file_name = st.session_state.download_file_name if st.session_state.download_file_name.endswith('.xlsx') else st.session_state.download_file_name+'.xlsx', 
                                        mime="text/xlsx", type="primary",
                                        use_container_width=True): 
                        #st.success(f"Dataset downloaded successfully in format XLSX as {st.session_state.download_file_name if st.session_state.download_file_name.endswith('.xslx') else st.session_state.download_file_name+'.xslx'}", icon="✅")
                        success_download_format = "XLSX"
                except Exception as e:   # if datetime error -> Excel does not support datetimes with timezones. Please ensure that datetimes are timezone unaware before writing to Excel.
                    st.error(str(e), icon="🚨")
            
            
            if success_download_format != "":   # if any download was successful
                st.success(f"Dataset downloaded successfully in format {success_download_format}. Filename, if not repeated: {st.session_state.download_file_name if st.session_state.download_file_name.endswith('.'+success_download_format.lower()) else st.session_state.download_file_name+'.'+success_download_format.lower()}", icon="✅")
                 
            
        else:    # just disabled button (to simulate blockage) and show error message
            col1, col2 = st.columns(2)
            with col1:
                st.button(label=":material/download: Download modified dataset as CSV", 
                            disabled=True, use_container_width=True)
            with col2:
                st.button(label=":material/download: Download modified dataset as JSON", 
                            disabled=True, use_container_width=True)
            col1, col2 = st.columns(2)
            with col1:
                st.button(label=":material/download: Download modified dataset as Parquet", 
                            disabled=True, use_container_width=True)
            with col2:
                st.button(label=":material/download: Download modified dataset as XLSX", 
                            disabled=True, use_container_width=True)
            
            st.error("Please, write a valid name for the file to download", icon="🚨")

    else:
        st.info("Please, upload a file first", icon=":material/help_center:")    # if no file uploaded, show info message