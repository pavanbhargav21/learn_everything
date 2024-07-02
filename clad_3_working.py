import streamlit as st
import pandas as pd
import os
from typing import Dict

# Constants
EXCEL_FILE = 'data.xlsx'
DATA_PATH = os.path.join(os.getcwd(), EXCEL_FILE)

# Define your fields here with their types
FIELDS: Dict[str, str] = {
    'Employee ID': 'number',
    'Global Career Band': 'text',
    'BF Level 1': 'text',
    'BF Level 2': 'text',
    'BF Level 3': 'text',
    'BF Level 4': 'text',
    'BF Level 5': 'text',
    'Department Name': 'text',
    'Work Location': 'text',
}

SKILL_FIELDS: Dict[str, str] = {f'Skill {i}': 'text' for i in range(1, 11)}

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

@st.cache(allow_output_mutation=True)
def load_data() -> pd.DataFrame:
    try:
        if os.path.exists(DATA_PATH):
            df = pd.read_excel(DATA_PATH)
            
            # Ensure all required columns exist
            for field in ALL_FIELDS.keys():
                if field not in df.columns:
                    df[field] = None
            
            # Ensure all number fields are of the correct type
            for field, field_type in ALL_FIELDS.items():
                if field_type == 'number':
                    df[field] = pd.to_numeric(df[field], errors='coerce').fillna(0).astype(int)
        else:
            df = pd.DataFrame(columns=ALL_FIELDS.keys())
    except Exception as e:
        st.error(f'Error loading data: {str(e)}')
        df = pd.DataFrame(columns=ALL_FIELDS.keys())
    return df

def save_to_excel(df: pd.DataFrame) -> None:
    try:
        df.to_excel(DATA_PATH, index=False)
        st.success('Data saved successfully.')
    except Exception as e:
        st.error(f'Error saving data: {str(e)}')

def main() -> None:
    st.markdown("<h1 class='main-header'>Employee Data Management</h1>", unsafe_allow_html=True)
    
    # Load data from Excel
    df = load_data()
    
    # Initialize session state
    if 'search_result' not in st.session_state:
        st.session_state.search_result = None
    if 'form_data' not in st.session_state:
        st.session_state.form_data = {}
    
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
            search_result = df[df['Employee ID'] == employee_id_search]
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
                        st.session_state.form_data[field] = int(value) if ALL_FIELDS[field] == 'number' else str(value)
                    else:
                        st.session_state.form_data[field] = 0 if ALL_FIELDS[field] == 'number' else ''
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
                st.session_state.form_data[field] = st.number_input(field, value=st.session_state.form_data.get(field, 0), min_value=0, key=field)
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
            for field, field_type in ALL_FIELDS.items():
                if field_type == 'number':
                    new_data[field] = int(new_data[field]) if new_data[field] else None
            
            if not df.empty and new_data['Employee ID'] in df['Employee ID'].values:
                index = df.index[df['Employee ID'] == new_data['Employee ID']].tolist()[0]
                df.loc[index] = pd.Series(new_data)
                st.success('Data updated successfully.')
            else:
                df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
                st.success('New data saved successfully.')
            
            save_to_excel(df)
            st.session_state.form_data = {}
            st.experimental_rerun()

    with col2:
        if st.button('Clear', key='clear_button', use_container_width=True):
            # Clear all form data fields directly
            st.session_state.form_data = {field: None for field in ALL_FIELDS}
            st.success('Form cleared.')
            st.experimental_rerun()

if __name__ == '__main__':
    main()
