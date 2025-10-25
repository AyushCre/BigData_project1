import pandas as pd
import streamlit as st
from typing import List, Tuple

def clean_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
    """
    Performs automated data cleaning on the input DataFrame.
    (Trims whitespace, converts numeric-strings, imputes missing values)
    """
    st.write("Initiating automated data cleaning process...")
    
    cleaned_df = df.copy()
    summary = []
    
    obj_cols = cleaned_df.select_dtypes(include=['object']).columns
    string_like_cols = []

    # Identify true string columns
    for col in obj_cols:
        if not cleaned_df[col].empty and cleaned_df[col].dropna().apply(type).eq(str).all():
            string_like_cols.append(col)

    # 1. Trim whitespace
    for col in string_like_cols:
        original_dtype = cleaned_df[col].dtype
        if pd.api.types.is_string_dtype(original_dtype):
             cleaned_df[col] = cleaned_df[col].str.strip()
    summary.append(f"✅ Trimmed whitespace from text columns.")

    # 2. Attempt to convert string columns to numeric
    converted_cols_summary = []
    obj_cols_after_strip = cleaned_df.select_dtypes(include=['object']).columns
    
    for col in obj_cols_after_strip:
        try:
            # Attempt to remove common currency symbols and commas
            if cleaned_df[col].str.contains(r'[$,₹]', regex=True, na=False).any():
                cleaned_df[col] = cleaned_df[col].replace({'\$': '', '₹': '', ',': ''}, regex=True)

            converted_col = pd.to_numeric(cleaned_df[col], errors='coerce')
            
            # Convert if a significant portion of the column is numeric
            if converted_col.notna().sum() / len(cleaned_df) > 0.5:
                cleaned_df[col] = converted_col
                converted_cols_summary.append(col)
        except Exception:
            continue
            
    if converted_cols_summary:
        summary.append(f"✅ Converted columns {converted_cols_summary} from text to numeric.")
    else:
        # This is expected if the PySpark script already cleaned the data
        summary.append("ℹ️ No text-based numeric columns found to convert (they might be clean already).")


    # 3. Impute missing values
    numeric_cols = cleaned_df.select_dtypes(include=['number']).columns
    filled_numeric = []
    for col in numeric_cols:
        if cleaned_df[col].isnull().sum() > 0:
            median_val = cleaned_df[col].median()
            cleaned_df[col].fillna(median_val, inplace=True)
            filled_numeric.append(col)
    if filled_numeric:
        summary.append(f"✅ Filled missing numeric values in {filled_numeric} with median.")

    categorical_cols = cleaned_df.select_dtypes(include=['object', 'category']).columns
    filled_cat = []
    for col in categorical_cols:
        if cleaned_df[col].isnull().sum() > 0:
            mode_val = cleaned_df[col].mode()
            if not mode_val.empty:
                cleaned_df[col].fillna(mode_val[0], inplace=True)
                filled_cat.append(col)
    if filled_cat:
         summary.append(f"✅ Filled missing categorical values in {filled_cat} with mode.")

    if not filled_numeric and not filled_cat:
        # This is also expected if the data is clean
        summary.append("👍 Data has no missing values to fill.")

    st.write("Data cleaning complete!")
    return cleaned_df, summary

