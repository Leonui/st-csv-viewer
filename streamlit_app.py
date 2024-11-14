import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path

# Set page config
st.set_page_config(
    page_title="CSV Data Viewer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
    <style>
    .stButton button {
        width: 100%;
    }
    div[data-testid="stDataFrame"] {
        width: 100%;
    }
    div[data-testid="stDataFrame"] > div {
        overflow-x: auto;
    }
    /* Improve sidebar styling */
    .css-1d391kg {
        padding-top: 1rem;
    }
    /* Improve icons */
    .sidebar .emoji {
        font-size: 24px;
        margin-right: 10px;
    }
    /* Better title spacing */
    h1 {
        margin-bottom: 2rem;
    }
    /* Improve search box */
    .stTextInput > div > div > input {
        padding: 10px 15px;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'data' not in st.session_state:
    st.session_state.data = None
if 'visible_columns' not in st.session_state:
    st.session_state.visible_columns = None
if 'current_file' not in st.session_state:
    st.session_state.current_file = None

def process_file(uploaded_file):
    """Process uploaded CSV file"""
    try:
        df = pd.read_csv(uploaded_file)
        return df
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
        return None

def highlight_search_term(data, search_term):
    """Create a Pandas Styler object with search term highlighting"""
    if not search_term:
        return data.style
    
    def highlight_cell(cell):
        try:
            cell_str = str(cell).lower()
            if search_term.lower() in cell_str:
                return 'background-color: yellow'
            return ''
        except:
            return ''
    
    return data.style.map(highlight_cell)

# Sidebar for controls
with st.sidebar:
    st.title("🛠️ Controls")
    
    # File upload
    st.header("📁 File Upload")
    uploaded_file = st.file_uploader(
        "Choose a CSV file",
        type=['csv', 'txt'],
        help="Upload a CSV file with the required columns"
    )

    if uploaded_file is not None and (
        st.session_state.current_file != uploaded_file.name
        or st.session_state.data is None
    ):
        df = process_file(uploaded_file)
        if df is not None:
            st.session_state.data = df
            st.session_state.current_file = uploaded_file.name
            st.session_state.visible_columns = {col: True for col in df.columns}
            st.success(f"Successfully loaded: {uploaded_file.name}")
    
    # Display settings
    if st.session_state.data is not None:
        with st.expander("⚙️ Display Settings", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Show All"):
                    st.session_state.visible_columns = {
                        col: True for col in st.session_state.data.columns
                    }
            with col2:
                if st.button("Hide All"):
                    st.session_state.visible_columns = {
                        col: False for col in st.session_state.data.columns
                    }
            
            st.markdown("---")
            
            # Column visibility checkboxes
            for col in st.session_state.data.columns:
                st.session_state.visible_columns[col] = st.checkbox(
                    col,
                    value=st.session_state.visible_columns[col]
                )

# Main content area
st.title("📊 CSV Data Viewer")

if st.session_state.data is not None:
    # Search functionality
    search_term = st.text_input(
        "🔍 Search in any column",
        help="Enter search term to filter data"
    )
    
    # Filter data based on search term
    if search_term:
        mask = st.session_state.data.astype(str).apply(
            lambda x: x.str.contains(search_term, case=False, na=False)
        ).any(axis=1)
        filtered_data = st.session_state.data[mask]
    else:
        filtered_data = st.session_state.data

    # Display data statistics
    st.markdown(f"Showing **{len(filtered_data)}** rows "
               f"{'matching search' if search_term else 'total'}")
    
    # Get visible columns
    visible_cols = [
        col for col in st.session_state.data.columns
        if st.session_state.visible_columns.get(col, True)
    ]
    
    if visible_cols:
        # Display the filtered data with visible columns
        display_data = filtered_data[visible_cols]
        
        # Calculate dynamic height (minimum 200px, maximum 800px)
        row_height = 35  # approximate height per row
        dynamic_height = min(max(len(display_data) * row_height + 50, 200), 800)
        
        # Display data with highlighting if search term exists
        if search_term:
            st.dataframe(
                highlight_search_term(display_data, search_term),
                use_container_width=True,
                height=dynamic_height
            )
        else:
            st.dataframe(
                display_data,
                use_container_width=True,
                height=dynamic_height
            )
    else:
        st.warning("Please select at least one column to display")
else:
    # Display upload prompt when no file is loaded
    st.info("📤 Please upload a CSV file using the sidebar")

# Add some spacing at the bottom
st.markdown("<br><br>", unsafe_allow_html=True)