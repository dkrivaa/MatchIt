import streamlit as st
import pandas as pd
import io
import re
import random
import numpy as np


def step1():
    st.title('MatchIT - Positions & Candidates')
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

    upper_dict = {'Position': []}
    lower_dict = {'Candidate': []}
    upper_variables, lower_variables = makefile(upperhand, lowerhand)
    upper_dict.update(upper_variables)
    lower_dict.update(lower_variables)

    df1 = pd.DataFrame(upper_dict)
    df2 = pd.DataFrame(lower_dict)

    # Download button to export data as Excel
    st.write("#### Download Excel file to enter data")
    st.write('(Remember to fill out both sheets)')

    with io.BytesIO() as buffer:
        # Use ExcelWriter to write multiple sheets to the buffer
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df1.to_excel(writer, sheet_name='Position Prefs', startrow=1, startcol=0, index=False)
            df2.to_excel(writer, sheet_name='Candidate Prefs', startrow=1, startcol=0, index=False)

            # Defining the layout of Excel file

            # Getting the column letter of last column in excel file (two sheets)
            u_letter = chr(ord('A') + upperhand)
            l_letter = chr(ord('A') + lowerhand)

            # Set column widths (adjust the widths as needed)
            workbook = writer.book
            worksheet1 = writer.sheets['Position Prefs']
            worksheet2 = writer.sheets['Candidate Prefs']
            worksheet1.set_column(f'A:{u_letter}', 15)
            worksheet2.set_column(f'A:{l_letter}', 15)

            # Setting height of first line
            worksheet1.set_row(0, 30)
            worksheet2.set_row(0, 30)

        # Writing explanations in first row

            worksheet1.write('a1', 'Name or Number of position')
            worksheet1.write('b1', 'Name or Number of 1st priority candidate')


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

        st.header('', divider='orange')

        # ______________________________________________________________________
        # Step 3
        st.write('### Step 3 - Press to MatchIT')

        matchIt = st.button('Press to Continue', type='primary')

        if matchIt:
            st.markdown('___')

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


            # The stable matching algorithm

            upperhand = 'position'
            lowerhand = 'candidate'

            tentative_appoint = []
            free_positions = []
            free_employees = []

            special_list = []

            def init_free_positions():
                for position in position_dict.keys():
                    free_positions.append(position)

            def init_free_employees():
                for employee in employee_dict.keys():
                    free_employees.append(employee)

            def stable_matching():
                if len(free_positions) > len(free_employees):
                    st.write('Not enough employees to fill all positions!')
                    quit()

                while len(free_positions) > 0:
                    for position in free_positions:
                        special_list.append(position)
                        if special_list.count(position) < 5:
                            begin_matching(position)
                        elif 5 <= special_list.count(position) < 10:
                            special_matching(position)
                        else:
                            st.write('Quitting due to inability to find solution for all positions')
                            quit()

            def begin_matching(position):

                # Function for calculating combined preferences
                def points(position, employee):
                    num_of_prefs_upperhand = st.session_state.num_of_prefs_upperhand
                    num_of_prefs_lowerhand = st.session_state.num_of_prefs_lowerhand

                    if position == 999:
                        position_points = 0
                    elif employee not in position_dict[position]:
                        position_points = 0
                    else:
                        position_points = 10 + num_of_prefs_upperhand - position_dict[position].index(employee)

                    if employee == 999:
                        employee_points = 0
                    elif position not in employee_dict[employee]:
                        employee_points = 0
                    else:
                        employee_points = 5.1 + num_of_prefs_lowerhand - employee_dict[employee].index(position)
                    points = position_points + employee_points

                    return points

                # Sorting position pref list by combined points of prefs
                best_list = []
                for employee in position_dict[position]:
                    point = points(position, employee)
                    best_list.append((employee, point))
                best_list = sorted(best_list, key=lambda x: x[1], reverse=True)
                temp_list = [x[0] for x in best_list]
                position_dict[position] = temp_list

                # Going through employees to find best match
                for employee in position_dict[position]:

                    if employee == 'employee0':
                        break

                    taken_match = [couple for couple in tentative_appoint if employee in couple]

                    if len(taken_match) == 0:
                        tentative_appoint.append([position, employee])
                        free_positions.remove(position)
                        free_employees.remove(employee)
                        break

                    elif len(taken_match) > 0:
                        current_position_points = points(taken_match[0][0], employee)
                        potential_position_points = points(position, employee)

                        if current_position_points >= potential_position_points:
                            pass

                        else:
                            free_positions.remove(position)
                            free_positions.append(taken_match[0][0])
                            taken_match[0][0] = position
                            break

            def special_matching(position):

                chosen_employee = [chosen for chosen in free_employees if position in employee_dict[chosen]]
                if len(chosen_employee) != 0:
                    tentative_appoint.append([position, chosen_employee[0]])
                    free_positions.remove(position)
                    free_employees.remove(chosen_employee[0])
                    # st.write(f'{chosen_employee} is tentatively appointed to {position}')

                else:
                    chosen_employee = random.choice(free_employees)
                    tentative_appoint.append([position, chosen_employee])
                    free_positions.remove(position)

            # The following statements are initializing the matching process
            init_free_positions()
            init_free_employees()
            stable_matching()

            # Showing results
            st.subheader('The optimal MATCH:')
            pos_count = 0
            emp_count = 0

            real_position_list = []
            real_candidate_list = []

            for i in range(0, len(df1)):
                real_candidate = (df2_original.iloc[:, 0][df2.iloc[:, 0] == tentative_appoint[i][1]]).iloc[0]
                real_position = (df1_original.iloc[:, 0][df2.iloc[:, 0] == tentative_appoint[i][0]]).iloc[0]
                real_position_list.append(real_position)
                real_candidate_list.append(real_candidate)
                # Writing the results to screen and adapt the text to context
                st.write(f'Appoint **{real_candidate}** to **{real_position}**')

                # Calculating how many got one of top wishes
                if tentative_appoint[i][1] in position_dict[tentative_appoint[i][0]]:
                    pos_count += 1

                if tentative_appoint[i][0] in employee_dict[tentative_appoint[i][1]]:
                    emp_count += 1

            # Making csv file of results to download
            pos = [sublist[0] for sublist in tentative_appoint]
            emp = [sublist[1] for sublist in tentative_appoint]
            # df_results = pd.DataFrame({'position': pos, 'employee': emp})
            # Code for the user entered positions and candidates (doesn't work with hebrew)
            df_results = pd.DataFrame({f'{upperhand}': real_position_list,
                                       f'{lowerhand}': real_candidate_list})

            def convert_df(df_any):
                return df_any.to_csv(index=False).encode('windows-1255')

            down_result = convert_df(df_results)

            st.download_button('Download results',
                               data=down_result,
                               file_name='results.csv',
                               mime='text/csv',
                               type='primary')

            # Summary data
            st.header('', divider='orange')

            st.subheader('Summary')
            st.write(f'Number of **{upperhand}s** that got one of top wishes: **{pos_count}** '
                     f'(out of **{len(tentative_appoint)}** open positions)')
            st.write(f'Number of **{lowerhand}s** that got one of top wishes: **{emp_count}** '
                     f'(out of **{possible}** that have corresponding wishes with positions)')


# __________________________________________________________________________________
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





