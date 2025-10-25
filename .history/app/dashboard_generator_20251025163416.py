import pandas as pd
import plotly.express as px
import streamlit as st
from typing import Optional

def _find_date_column(df: pd.DataFrame) -> Optional[str]:
    """Helper to find the first suitable date column."""
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            return col
            
    # If no native datetime, try converting objects
    for col in df.columns:
        if df[col].dtype == 'object':
            try:
                temp_col = pd.to_datetime(df[col], errors='coerce')
                if temp_col.notna().sum() / len(df) > 0.7:
                    df[col] = temp_col 
                    return col
            except (ValueError, TypeError, OverflowError):
                continue 
    return None

def create_dashboard(df: pd.DataFrame):
    """
    Generates and displays the main dashboard.
    """
    st.header("📊 Automated Dashboard")
    st.write("An interactive dashboard generated from your data.")

    # Get column lists
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    date_col = _find_date_column(df)

    # --- ROW 1: KPIs ---
    st.subheader("Key Performance Indicators")
    if numeric_cols:
        kpi_count = min(4, len(numeric_cols))
        kpi_cols = st.columns(kpi_count)
        
        for i, col in enumerate(kpi_cols):
            col_name = numeric_cols[i]
            total = df[col_name].sum()
            col.metric(label=f"Total {col_name}", value=f"{total:,.2f}")
    else:
        st.info("No numeric columns available for KPIs.")
    
    st.markdown("---")

    # --- ROW 2: Main Charts (Trend & Pie) ---
    left_col, right_col = st.columns([3, 2]) 

    with left_col:
        # Time-Series Chart
        if date_col and numeric_cols:
            st.subheader("Trend Analysis")
            
            default_trend_col = next((c for c in numeric_cols if 'sales' in c.lower()), numeric_cols[0])
            
            sel_num_col = st.selectbox(
                "Select feature for trend:",
                options=numeric_cols,
                index=numeric_cols.index(default_trend_col)
            )
            
            if sel_num_col:
                df_sorted = df.dropna(subset=[date_col]).sort_values(by=date_col)
                
                if not df_sorted.empty:
                    time_delta = df_sorted[date_col].max() - df_sorted[date_col].min()

                    if time_delta.days > 365 * 2:
                        period, period_name = 'Y', 'Year'
                    elif time_delta.days > 90:
                        period, period_name = 'M', 'Month'
                    elif time_delta.days > 7:
                        period, period_name = 'W', 'Week'
                    else:
                        period, period_name = 'D', 'Day'
                    
                    st.info(f"💡 Data automatically grouped by **{period_name}**.")

                    df_trend = df.groupby(df[date_col].dt.to_period(period))[sel_num_col].mean().reset_index()
                    df_trend[date_col] = df_trend[date_col].dt.to_timestamp() 

                    fig_line = px.line(df_trend, x=date_col, y=sel_num_col, 
                                       title=f"Average {sel_num_col} by {period_name}",
                                       markers=True)
                    st.plotly_chart(fig_line, use_container_width=True)
                else:
                    st.warning("No valid date data found to plot trend.")
        
        elif cat_cols:
            st.subheader("Categorical Counts")
            default_bar_col = next((c for c in cat_cols if 1 < df[c].nunique() < 20), cat_cols[0])
            
            bar_choice = st.selectbox(
                "Select column for Bar Chart:",
                options=cat_cols,
                index=cat_cols.index(default_bar_col)
            )
            
            bar_counts = df[bar_choice].value_counts().nlargest(15).reset_index()
            fig_bar = px.bar(bar_counts, x=bar_choice, y='count',
                             title=f"Top 15 Counts for '{bar_choice}'")
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("No suitable date or categorical columns to plot here.")

    with right_col:
        # Pie Chart
        st.subheader("Distribution")
        if cat_cols:
            default_pie_col = next((c for c in cat_cols if 1 < df[c].nunique() < 10), cat_cols[0])
            
            pie_choice = st.selectbox(
                "Select column for Pie Chart:",
                options=cat_cols,
                index=cat_cols.index(default_pie_col)
            )
            
            pie_counts = df[pie_choice].value_counts()
            fig_pie = px.pie(pie_counts, names=pie_counts.index, values=pie_counts.values,
                             title=f"Distribution of {pie_choice}")
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No categorical columns for a pie chart.")

    st.markdown("---")
    
    # --- ROW 3: Numeric Analysis (Histogram & Heatmap) ---
    st.subheader("Numeric Feature Analysis")
    
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Histogram")
        if numeric_cols:
            hist_col = st.selectbox("Select feature for Histogram", numeric_cols, index=0)
            fig_hist = px.histogram(df, x=hist_col, title=f"Distribution of {hist_col}")
            st.plotly_chart(fig_hist, use_container_width=True)
        else:
            st.info("No numeric columns for a histogram.")
            
    with col2:
        st.subheader("Correlation Heatmap")
        if len(numeric_cols) >= 2:
            corr_matrix = df[numeric_cols].corr(numeric_only=True)
            fig_heatmap = px.imshow(corr_matrix, text_auto=True,
                                    title="Correlation Heatmap",
                                    color_continuous_scale='RdBu_r', 
                                    aspect="auto")
            st.plotly_chart(fig_heatmap, use_container_width=True)
        else:
            st.info("Need at least 2 numeric columns for a heatmap.")
            
    st.markdown("---")

    # --- ROW 4: Scatter Plot ---
    if len(numeric_cols) >= 2:
        st.subheader(f"Relationship Analysis")
        
        sc_col1, sc_col2, sc_col3 = st.columns(3)
        with sc_col1:
            x_axis = st.selectbox("Select X-axis", numeric_cols, index=0)
        with sc_col2:
            y_axis = st.selectbox("Select Y-axis", numeric_cols, index=1)
        with sc_col3:
            color_axis = st.selectbox("Color by (optional)", [None] + cat_cols)

        fig_scatter = px.scatter(df, x=x_axis, y=y_axis, color=color_axis,
                                 title=f"Relationship between {x_axis} and {y_axis}")
        st.plotly_chart(fig_scatter, use_container_width=True)

