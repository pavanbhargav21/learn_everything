import streamlit as st
import pandas as pd
import sqlite3
from typing import Dict

# Constants
DATABASE_FILE = 'employee_data.db'
conn = sqlite3.connect(DATABASE_FILE, check_same_thread=False)

# Define your fields here with their types
FIELDS: Dict[str, str] = {
    'EmployeeID': 'INTEGER',
    'GlobalCareerBand': 'TEXT',
    'BFLevel1': 'TEXT',
    'BFLevel2': 'TEXT',
    'BFLevel3': 'TEXT',
    'BFLevel4': 'TEXT',
    'BFLevel5': 'TEXT',
    'DepartmentName': 'TEXT',
    'WorkLocation': 'TEXT',
}

SKILL_FIELDS: Dict[str, str] = {f'Skill{i}': 'TEXT' for i in range(1, 11)}

# Combine all fields
ALL_FIELDS: Dict[str, str] = {**FIELDS, **SKILL_FIELDS}

# Custom CSS to improve the look and feel
custom_css = """
<style>
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
        padding: 2rem;
        background-color: #f0f2f6;
    }
    .main-header {
        color: #0e1117;
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 2rem;
        text-align: center;
        background-color: #4CAF50;
        color: white;
        padding: 20px;
        border-radius: 10px;
    }
    .subheader {
        color: #0e1117;
        font-size: 1.5rem;
        font-weight: 600;
        margin-top: 2rem;
        margin-bottom: 1rem;
        background-color: #2196F3;
        color: white;
        padding: 10px;
        border-radius: 5px;
    }
    .stButton>button {
        width: 100%;
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
    }
    .stTextInput>div>div>input, .stNumberInput>div>div>input {
        background-color: white;
        border: 1px solid #ddd;
        border-radius: 5px;
    }
    .search-container {
        display: flex;
        align-items: flex-end;
        gap: 10px;
    }
    .search-container > div {
        flex: 1;
    }
    .stDataFrame {
        border: 1px solid #ddd;
        border-radius: 5px;
        overflow: hidden;
    }
</style>
"""

st.set_page_config(page_title="Employee Data Management", layout="wide")
st.markdown(custom_css, unsafe_allow_html=True)

def create_table_if_not_exists():
    cursor = conn.cursor()
    columns = ', '.join([f'{key} {value}' for key, value in ALL_FIELDS.items()])
    query = f"CREATE TABLE IF NOT EXISTS EmployeeData ({columns})"
    cursor.execute(query)
    conn.commit()

def load_data() -> pd.DataFrame:
    try:
        create_table_if_not_exists()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM EmployeeData")
        rows = cursor.fetchall()
        df = pd.DataFrame(rows, columns=ALL_FIELDS.keys())
    except Exception as e:
        st.error(f'Error loading data: {str(e)}')
        df = pd.DataFrame(columns=ALL_FIELDS.keys())
    return df

def save_to_database(new_data: Dict[str, str]) -> None:
    try:
        create_table_if_not_exists()
        cursor = conn.cursor()
        
        # Check if EmployeeID exists to decide between INSERT and UPDATE
        employee_id = new_data['EmployeeID']
        if pd.notna(employee_id) and cursor.execute(f"SELECT 1 FROM EmployeeData WHERE EmployeeID = ?", (employee_id,)).fetchone():
            # Update existing record
            update_query = ", ".join([f"{key} = ?" for key in new_data.keys()])
            query = f"UPDATE EmployeeData SET {update_query} WHERE EmployeeID = ?"
            cursor.execute(query, (*new_data.values(), employee_id))
            st.success('Data updated successfully.')
        else:
            # Insert new record
            columns = ', '.join(new_data.keys())
            placeholders = ', '.join(['?'] * len(new_data))
            query = f"INSERT INTO EmployeeData ({columns}) VALUES ({placeholders})"
            cursor.execute(query, tuple(new_data.values()))
            st.success('New data saved successfully.')
        
        conn.commit()
    except Exception as e:
        st.error(f'Error saving data: {str(e)}')

def main() -> None:
    st.markdown("<h1 class='main-header'>Employee Data Management</h1>", unsafe_allow_html=True)
    
    # Load data from SQLite
    df = load_data()
    
    # Initialize session state
    if 'search_result' not in st.session_state:
        st.session_state.search_result = None
    if 'form_data' not in st.session_state:
        st.session_state.form_data = {key: None for key in ALL_FIELDS.keys()}
    
    # Search form
    st.markdown("<h2 class='subheader'>Search by Employee ID</h2>", unsafe_allow_html=True)
    with st.container():
        col1, col2 = st.columns([3, 1])
        with col1:
            employee_id_search = st.number_input('Employee ID:', min_value=0, step=1, key='search_input')
        with col2:
            search_button = st.button('Search', key='search_button', use_container_width=True)
    
    if search_button:
        if employee_id_search == 0:
            st.warning('Please enter a valid Employee ID.')
        else:
            search_result = df[df['EmployeeID'] == employee_id_search]
            if not search_result.empty:
                st.dataframe(search_result, use_container_width=True)
                st.session_state.search_result = search_result
                st.success('Data found for Employee ID.')
            else:
                st.warning('No data found for Employee ID.')
                st.session_state.search_result = None

    # Display edit button if search result exists
    if st.session_state.search_result is not None:
        if st.button('Edit', key='edit_button', use_container_width=True):
            search_result = st.session_state.search_result
            if not search_result.empty:
                for field in ALL_FIELDS:
                    value = search_result.iloc[0][field]
                    if pd.notna(value):
                        st.session_state.form_data[field] = value
                    else:
                        st.session_state.form_data[field] = None
                st.success('Form filled with search result.')
                st.experimental_rerun()
            else:
                st.warning('No data found for Employee ID.')

    # Data entry / edit form
    st.markdown("<h2 class='subheader'>Employee Data </h2>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    for i, (field, field_type) in enumerate(FIELDS.items()):
        with col1 if i < len(FIELDS) // 2 else col2:
            if field_type == 'number':
                st.session_state.form_data[field] = st.number_input(field, value=st.session_state.form_data.get(field, None), min_value=0, key=field)
            else:
                st.session_state.form_data[field] = st.text_input(field, value=st.session_state.form_data.get(field, ''), key=field)

    st.markdown("<h3 class='subheader'>Skills</h3>", unsafe_allow_html=True)
    skills_col1, skills_col2 = st.columns(2)
    for i, (skill_field, field_type) in enumerate(SKILL_FIELDS.items()):
        with skills_col1 if i < len(SKILL_FIELDS) // 2 else skills_col2:
            st.session_state.form_data[skill_field] = st.text_input(skill_field, value=st.session_state.form_data.get(skill_field, ''), key=skill_field)

    # Save and Clear buttons
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        if st.button('Save', key='save_button', use_container_width=True):
            new_data = {field: st.session_state.form_data[field] for field in ALL_FIELDS}
            save_to_database(new_data)
            st.session_state.form_data = {key: None for key in ALL_FIELDS.keys()}
            st.experimental_rerun()

    with col2:
        if st.button('Clear', key='clear_button', use_container_width=True):
            st.session_state.form_data = {key: None for key in ALL_FIELDS.keys()}
            st.success('Form cleared.')
            st.rerun()

if __name__ == '__main__':
    main()
