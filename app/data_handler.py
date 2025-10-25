import pandas as pd
import streamlit as st
from typing import Optional

def load_data(uploaded_file) -> Optional[pd.DataFrame]:
    """
    Reads an uploaded file (CSV, Excel, or JSON) and loads it into a pandas DataFrame.
    """
    df = None
    try:
        file_extension = uploaded_file.name.split('.')[-1].lower()
        
        if file_extension == 'csv':
            df = pd.read_csv(uploaded_file)
        elif file_extension in ['xlsx', 'xls']:
            df = pd.read_excel(uploaded_file)
        elif file_extension == 'json':
            df = pd.read_json(uploaded_file)
        
        if df is not None:
            st.success("Dataset loaded successfully!")
            return df
        else:
            st.error("Unsupported file format.")
            return None
    except Exception as e:
        st.error(f"Error reading file: {e}")
        return None

