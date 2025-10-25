import streamlit as st
from data_handler import load_data
from data_cleaner import clean_data
from dashboard_generator import create_dashboard
from insights_generator import generate_insights

def main():
    """
    Main app function.
    """
    st.set_page_config(
        page_title="Auto Dashboard Generator",
        page_icon="📊",
        layout="wide"
    )

    st.title("🚀 Auto Dashboard Generator")
    st.write("Upload your data file (CSV, Excel, or JSON) to get started.")
    # This info box is now fully in English
    st.info("Note: For large files, run the 'process_data.py' script first and upload the 'cleaned_sample.csv' file here.")


    uploaded_file = st.file_uploader(
        "Upload your (preferably cleaned sample) data file here", 
        type=['csv', 'xlsx', 'xls', 'json']
    )

    if uploaded_file:
        df_raw = load_data(uploaded_file)
        
        if df_raw is None:
            st.error("Could not load the file. Please try again.")
            return 

        st.markdown("---")
        
        # --- Cleaning ---
        st.subheader("🧹 Automated Data Cleaning")
        df_cleaned, cleaning_summary = clean_data(df_raw)
        
        with st.expander("Click to see the data cleaning summary"):
            for action in cleaning_summary:
                st.markdown(f"- {action}")
        
        # We will always use the cleaned data
        data = df_cleaned
        
        st.markdown("---")
        
        # --- Data Preview ---
        st.subheader("Data Preview")
        st.dataframe(data.head())
        
        st.markdown("---")

        # --- Insights ---
        st.subheader("🔍 Quick Insights")
        with st.expander("Click to see high-level insights"):
            insights = generate_insights(data) 
            for insight in insights:
                st.markdown(f"- {insight}")

        st.markdown("---")
        
        # --- Dashboard ---
        create_dashboard(data)

if __name__ == "__main__":
    main()

