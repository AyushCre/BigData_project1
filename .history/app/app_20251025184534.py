import streamlit as st
from data_handler import load_data
from data_cleaner import clean_data
from dashboard_generator import create_dashboard
from insights_generator import generate_insights

# --- Cached Functions ---
# Yeh functions data ko memory (cache) mein store kar denge.
# Isse app crash nahi hoga jab aap dropdown badlenge,
# kyunki yeh data ko baar-baar load ya clean nahi karega.

@st.cache_data  # Cache the data loading
def cached_load_data(file):
    """Cached function to load data."""
    return load_data(file)

@st.cache_data  # Cache the data cleaning
def cached_clean_data(_df):
    """Cached function to clean data."""
    # Hum _df ka istemaal karte hain taaki cache changes ko pehchaan sake
    return clean_data(_df)

@st.cache_data  # Cache the insight generation
def cached_generate_insights(_df):
    """Cached function to generate insights."""
    return generate_insights(_df)

# NOTE: Hum create_dashboard ko cache nahi kar sakte
# kyunki woh Streamlit commands (st.write, st.selectbox) ka istemaal karta hai.
# Caching data return karne waale functions ke liye hota hai, UI ke liye nahi.

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
    st.info("Note: For large files, run the 'process_data.py' script first and upload the 'cleaned_sample.csv' file here.")


    uploaded_file = st.file_uploader(
        "Upload your (preferably cleaned sample) data file here", 
        type=['csv', 'xlsx', 'xls', 'json']
    )

    if uploaded_file:
        # Ab hum CACHED function ka istemaal karenge
        df_raw = cached_load_data(uploaded_file)
        
        if df_raw is None:
            st.error("Could not load the file. Please try again.")
            return 

        st.markdown("---")
        
        # --- Cleaning ---
        st.subheader("🧹 Automated Data Cleaning")
        # (Yeh bache hue missing values ko handle karega)
        
        # Hum CACHED function ka istemaal karenge
        df_cleaned, cleaning_summary = cached_clean_data(df_raw)
        
        with st.expander("Click to see the data cleaning summary"):
            for action in cleaning_summary:
                st.markdown(f"- {action}")

        # --- Toggle Button ---
        use_cleaned_data = st.toggle(
            "Apply automated cleaning (Impute missing values)",
            value=True, # Default is 'On'
            help="Turn this off to use the original, raw data for the dashboard."
        )

        # Main dataframe to be used for charts
        if use_cleaned_data:
            data = df_cleaned
            st.caption("Displaying cleaned and imputed data. 👇")
        else:
            data = df_raw
            st.caption("Displaying raw, original data (as uploaded). 👇")

        
        st.markdown("---")
        
        # --- Data Preview ---
        st.subheader("Data Preview")
        st.dataframe(data.head())
        
        st.markdown("---")

        # --- Insights ---
        st.subheader("🔍 Quick Insights")
        with st.expander("Click to see high-level insights"):
            # Hum CACHED function ka istemaal karenge
            insights = cached_generate_insights(data) 
            for insight in insights:
                st.markdown(f"- {insight}")

        st.markdown("---")
        
        # --- Dashboard ---
        # Yeh function abhi bhi run hoga, lekin isko jo data
        # mil raha hai (df_raw, df_cleaned) woh cache se aa raha hai,
        # jisse bahut saari memory aur time bachta hai.
        create_dashboard(data)

if __name__ == "__main__":
    main()

