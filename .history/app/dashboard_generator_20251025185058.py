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
                # Try to convert, but be careful
                temp_col = pd.to_datetime(df[col], errors='coerce')
                # Check if conversion was successful for most rows
                if temp_col.notna().sum() / len(df) > 0.7:
                    df[col] = temp_col # Convert in place
                    # TODO: Maybe add a warning to user that we converted this col?
                    return col
            except (ValueError, TypeError, OverflowError):
                continue # Skip columns that fail conversion
    return None

def create_dashboard(df: pd.DataFrame):
    """
    Generates and displays the main dashboard.
    """
    st.header("📊 Automated Dashboard")
    st.write("An interactive dashboard generated from your data.")

    # Get column lists
    num_cols = df.select_dtypes(include=['number']).columns.tolist()
    cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    date_col = _find_date_column(df)

    # --- ROW 1: KPIs ---
    st.subheader("Key Performance Indicators")
    if num_cols:
        kpi_n = min(4, len(num_cols)) # Show max 4 KPIs
        kpi_columns = st.columns(kpi_n)
        
        for i, col in enumerate(kpi_columns):
            kpi_col_name = num_cols[i]
            total = df[kpi_col_name].sum()
            col.metric(label=f"Total {kpi_col_name}", value=f"{total:,.2f}")
    else:
        st.info("No numeric columns available for KPIs.")
    
    st.markdown("---")

    # --- ROW 2: Main Charts (Trend & Pie) ---
    col1, col2 = st.columns([3, 2]) 

    with col1:
        # Time-Series Chart
        if date_col and num_cols:
            st.subheader("Trend Analysis")
            
            # Try to find a good default metric
            default_metric = next((c for c in num_cols if 'sales' in c.lower()), num_cols[0])
            
            metric_choice = st.selectbox(
                "Select feature for trend:",
                options=num_cols,
                index=num_cols.index(default_metric)
            )
            
            if metric_choice:
                sorted_df = df.dropna(subset=[date_col]).sort_values(by=date_col)
                
                if not sorted_df.empty:
                    delta = sorted_df[date_col].max() - sorted_df[date_col].min()

                    # Auto-grouping logic
                    if delta.days > 365 * 2:
                        agg_period, period_label = 'Y', 'Year'
                    elif delta.days > 90:
                        agg_period, period_label = 'M', 'Month'
                    elif delta.days > 7:
                        agg_period, period_label = 'W', 'Week'
                    else:
                        agg_period, period_label = 'D', 'Day'
                    
                    st.info(f"💡 Data automatically grouped by **{period_label}**.")

                    # Group and plot
                    trend_data = df.groupby(df[date_col].dt.to_period(agg_period))[metric_choice].mean().reset_index()
                    trend_data[date_col] = trend_data[date_col].dt.to_timestamp()

                    fig = px.line(trend_data, x=date_col, y=metric_choice, 
                                       title=f"Average {metric_choice} by {period_label}",
                                       markers=True)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("No valid date data found to plot trend.")
        
        elif cat_cols:
            # Fallback: If no date col, show a Bar chart here
            st.subheader("Categorical Counts")
            default_bar = next((c for c in cat_cols if 1 < df[c].nunique() < 20), cat_cols[0])
            
            bar_col = st.selectbox(
                "Select column for Bar Chart:",
                options=cat_cols,
                index=cat_cols.index(default_bar)
            )
            
            st.info("Displaying top 15 values. Others are grouped into 'Other'.")
            counts = df[bar_col].value_counts()
            
            if len(counts) > 15:
                top_n = counts.nlargest(15)
                other_total = counts.nsmallest(len(counts) - 15).sum()
                other_row = pd.Series([other_total], index=['Other'])
                final_bar_data = pd.concat([top_n, other_row])
            else:
                final_bar_data = counts
                
            final_bar_data = final_bar_data.reset_index()
            final_bar_data.columns = [bar_col, 'count'] # Force-rename columns

            fig = px.bar(final_bar_data, x=bar_col, y='count',
                             title=f"Top 15 Counts for '{bar_col}'")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No suitable date or categorical columns to plot here.")

    with col2:
        # Pie Chart
        st.subheader("Distribution")
        if cat_cols:
            # Find a good default column for pie (few unique values)
            default_pie = next((c for c in cat_cols if 1 < df[c].nunique() < 10), cat_cols[0])
            
            pie_col = st.selectbox(
                "Select column for Pie Chart:",
                options=cat_cols,
                index=cat_cols.index(default_pie)
            )
            
            st.info("Displaying top 10 values. Others are grouped into 'Other'.")
            
            counts = df[pie_col].value_counts()
            
            if len(counts) > 10:
                top_n = counts.nlargest(10)
                other_total = counts.nsmallest(len(counts) - 10).sum()
                other_row = pd.Series([other_total], index=['Other'])
                final_pie_data = pd.concat([top_n, other_row])
            else:
                final_pie_data = counts
            
            final_pie_data = final_pie_data.reset_index()
            final_pie_data.columns = [pie_col, 'count'] # Force-rename

            fig = px.pie(final_pie_data, names=pie_col, values='count',
                             title=f"Distribution of {pie_col} (Top 10)")
            
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No categorical columns for a pie chart.")

    st.markdown("---")
    
    # --- ROW 3: Numeric Analysis (Histogram & Heatmap) ---
    st.subheader("Numeric Feature Analysis")
    
    hist_col, heatmap_col = st.columns(2)

    with hist_col:
        st.subheader("Histogram")
        if num_cols:
            hist_choice = st.selectbox("Select feature for Histogram", num_cols, index=0)
            fig = px.histogram(df, x=hist_choice, title=f"Distribution of {hist_choice}")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No numeric columns for a histogram.")
            
    with heatmap_col:
        st.subheader("Correlation Heatmap")
        if len(num_cols) >= 2:
            corr = df[num_cols].corr(numeric_only=True)
            fig = px.imshow(corr, text_auto=True,
                                    title="Correlation Heatmap",
                                    color_continuous_scale='RdBu_r', # Red-Blue scale
                                    aspect="auto")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Need at least 2 numeric columns for a heatmap.")
            
    st.markdown("---")

    # --- ROW 4: Scatter Plot ---
    if len(num_cols) >= 2:
        st.subheader(f"Relationship Analysis")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            x_ax = st.selectbox("Select X-axis", num_cols, index=0)
        with col2:
            y_ax = st.selectbox("Select Y-axis", num_cols, index=1)
        with col3:
            color_choice = st.selectbox("Color by (optional)", [None] + cat_cols)

        fig = px.scatter(df, x=x_ax, y=y_ax, color=color_choice,
                                 title=f"Relationship between {x_ax} and {y_ax}")
        st.plotly_chart(fig, use_container_width=True)

