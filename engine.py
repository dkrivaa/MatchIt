import streamlit as st
import pandas as pd
import io


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

    file = st.file_uploader('Choose Excel file', 'xlsx')




# Help function for step 1
def makefile(upperhand, lowerhand):
    upper_variables = {f"Position_pref_{i}": [] for i in range(1, upperhand + 1)}
    lower_variables = {f"Candidate_pref_{j}": [] for j in range(1, lowerhand + 1)}
    return upper_variables, lower_variables