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
    st.write('### Step 2 - Upload Excel file (after filling in data)')

    file = st.file_uploader('Choose Excel file', type=['xlsx', 'xls'])
    if file is not None:
        df1 = pd.read_excel(file, sheet_name='Position Prefs')
        df2 = pd.read_excel(file, sheet_name='Candidate Prefs')
        st.write('##### Your file was uploaded successfully')

        st.write(df1)

        df1_original = df1.copy()
        df2_original = df2.copy()


        # Making values into integers:
        # relevant position by index
        df1['position'] = df1.index + 1
        # preferences by extracting number from string (if string)
        for column in df1.columns[1:]:
            df1[column] = df1[column].apply(extract_numbers_from_string, df=df2_original)

        # Making values into integers:
        # relevant position by index
        df2['candidate'] = df2.index + 1
        # preferences by extracting number from string (if string)
        for column in df2.columns[1:]:
            df2[column] = df2[column].apply(extract_numbers_from_string, df=df1_original)

        st.write(df1)



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
        if len(str(input_string)) > 3:
            index_in_df = df[df.iloc[:, 0] == input_string].index.tolist()
            return index_in_df[0] + 1 if index_in_df else None
        else:
            return input_string

