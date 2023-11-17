import streamlit as st
import pandas as pd
import io
import re


def step1():
    st.title('Match Positions & Candidates')
    st.markdown('___')

    # Step 1
    st.write('### Step 1 - Make Excel file for download')
    col1, col2 = st.columns(2)
    with col1:
        upperhand = st.number_input('Max preferences Employer:', min_value=1)
        # st.write(upperhand)
    with col2:
        lowerhand = st.number_input('Max preferences Employee:', min_value=1)
        # st.write(lowerhand)

    upper_dict = {'position': []}
    lower_dict = {'candidate': []}
    upper_variables, lower_variables = makefile(upperhand, lowerhand)
    upper_dict.update(upper_variables)
    lower_dict.update(lower_variables)
    #
    # with col1:
    #     st.write(upper_dict)
    # with col2:
    #     st.write(lower_dict)

    df1 = pd.DataFrame(upper_dict)
    df2 = pd.DataFrame(lower_dict)

    # Download button to export data as Excel
    st.write("#### Download Excel file to enter data")
    st.write('(Remember to fill out both sheets)')

    with io.BytesIO() as buffer:
        # Use ExcelWriter to write multiple sheets to the buffer
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df1.to_excel(writer, sheet_name='Position Prefs', index=False)
            df2.to_excel(writer, sheet_name='Candidate Prefs', index=False)

        buffer.seek(0)

        st.download_button(
            label="Download Excel",
            data=buffer.read(),
            file_name="Preferences.xlsx",
            type='primary',
            key="download_button",
        )

    st.markdown('___')



def step2():
    # Step 2
    st.write('### Step 2 - Upload Your Excel file (after filling in data)')

    file = st.file_uploader('Choose Your Excel file', type=['xlsx', 'xls'])
    if file is not None:
        df1 = pd.read_excel(file, sheet_name='Position Prefs').fillna(999)
        df2 = pd.read_excel(file, sheet_name='Candidate Prefs').fillna(999)

        df1_original = df1.copy()
        df2_original = df2.copy()

        # Making values into integers:
        # relevant position by index
        df1.iloc[:, 0] = df1.index + 1
        # preferences by extracting number from string (if string)
        for column in df1.columns[1:]:
            df1[column] = df1[column].apply(extract_numbers_from_string, df=df2_original)

        # Making values into integers:
        # relevant employee by index
        df2.iloc[:, 0] = df2.index + 1
        # preferences by extracting number from string (if string)
        for column in df2.columns[1:]:
            df2[column] = df2[column].apply(extract_numbers_from_string, df=df1_original)

        # Checking integrity of data in file
        # Position data:
        # checking the lack of identical preference entries
        test1 = (df1.iloc[:, 1:].apply(lambda row: row.dropna().nunique() == len(row), axis=1))
        if all(test1):
            pass
        else:
            row_index = [i for i in range(0, len(test1)) if test1[i] is False]
            st.error(f'Error: Identical preference entries for position: '
                     f'{df1_original.iloc[row_index[0]][0]}. Please correct the error '
                     f'and upload file again.')
            exit()

        # checking that all data is ok (first condition = only numbers, second condition = valid preferences)
        if ((df1.applymap(lambda x: isinstance(x, int)).all().all()) and
                (df1.applymap(lambda y: (y < len(df2) + 1) or (y == 999))).all().all()):
            pass
        else:
            st.write('Something is wrong, most probably an invalid preference for one of the positions. '
                     'Please chck your file, correct the mistake and upload the file again')
            exit()

        # Employee data:
        # checking the lack of identical preference entries
        test2 = (df2.iloc[:, 1:].apply(lambda row: row.dropna().nunique() == len(row), axis=1))
        if all(test2):
            pass
        else:
            row_index = [i for i in range(0, len(test2)) if test2[i] is False]
            st.error(f'Error: Identical preference entries for employee: '
                     f'{df2_original.iloc[row_index[0]][0]}. Please correct the error '
                     f'and upload file again.')
            exit()

        # checking that all data is ok (first condition = only numbers, second condition = valid preferences)
        if ((df2.applymap(lambda x: isinstance(x, int)).all().all()) and
                (df2.applymap(lambda y: (y < len(df2) + 1) or (y == 999))).all().all()):
            pass
        else:
            st.write('Something is wrong, most probably an invalid preference for one of the employees. '
                     'Please check your file, correct the mistake and upload the file again')
            exit()

        st.write('##### Your file was uploaded successfully')

        st.markdown('___')

        # ______________________________________________________________________
        # Step 3
        st.write('### Step 3 - Press to MatchIT')

        # Making data ready for MATCHING process
        position_list = df1.iloc[:, 0].tolist()
        position_pref_list = list(zip(*df1.iloc[:, 1:].values.T))
        position_dict = dict(zip(position_list, position_pref_list))

        employee_list = df2.iloc[:, 0].tolist()
        employee_pref_list = list(zip(*df2.iloc[:, 1:].values.T))
        employee_dict = dict(zip(employee_list, employee_pref_list))

        # Getting the number of max preferences for upperhand (positions) and lowerhand (employees)
        num_of_prefs_upperhand = len(max(position_pref_list, key=len))
        num_of_prefs_lowerhand = len(max(employee_pref_list, key=len))

        if num_of_prefs_upperhand not in st.session_state:
            st.session_state.num_of_prefs_upperhand = num_of_prefs_upperhand

        if num_of_prefs_lowerhand not in st.session_state:
            st.session_state.num_of_prefs_lowerhand = num_of_prefs_lowerhand

        # Calculating how many employees have matching preferences with positions
        possible = 0
        for employee in employee_list:
            for position in employee_dict[employee]:
                try:
                    if employee in position_dict[position]:
                        possible += 1
                        break
                except KeyError:
                    pass

        st.write(possible)


# Help function for step 1
def makefile(upperhand, lowerhand):
    upper_variables = {f"Position_pref_{i}": [] for i in range(1, upperhand + 1)}
    lower_variables = {f"Candidate_pref_{j}": [] for j in range(1, lowerhand + 1)}
    return upper_variables, lower_variables


def extract_numbers_from_string(input_string, df):
    if isinstance(input_string, str):
        # Use regular expression to find all numbers in the string
        numbers = re.findall(r'\d+', input_string)

        # If there are numbers, return the first one
        if numbers:
            return int(numbers[0])
        else:
            # If there are no numbers, look up the index in df2
            index_in_df = df[df.iloc[:, 0] == input_string].index.tolist()
            return index_in_df[0] + 1 if index_in_df else None
    else:
        if len(str(input_string)) > 4:
            index_in_df = df[df.iloc[:, 0] == input_string].index.tolist()
            return index_in_df[0] + 1 if index_in_df else None
        else:
            return input_string


def check_integrity_of_data(df, df_original ):
    # check that all entries are now integers
    df.applymap(lambda x: isinstance(x, int)).all().all()


