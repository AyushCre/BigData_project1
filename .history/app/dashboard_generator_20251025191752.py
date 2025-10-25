import pandas as pd
import plotly.express as px
import streamlit as st
from typing import Optional

def _find_date_column(df: pd.DataFrame) -> Optional[str]:
    """
    Helper to find the first suitable date column.
    Tries to convert object columns if they look like dates.
    """
    # First, check for actual datetime types
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
                    return col
            except (ValueError, TypeError, OverflowError):
                continue # Skip columns that fail conversion
    return None

def create_dashboard(df: pd.DataFrame):
    """
    Generates and displays the main dashboard.
    """
    st.header("📊 Interactive Dashboard")

    # --- Column Setup ---
    try:
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        date_col = _find_date_column(df)
    except Exception as e:
        st.error(f"Error processing DataFrame columns: {e}")
        return

    # --- ROW 1: KPIs ---
    st.subheader("Key Performance Indicators")
    if numeric_cols:
        kpi_count = min(4, len(numeric_cols))
        if kpi_count > 0:
            kpi_cols = st.columns(kpi_count)
            for i in range(kpi_count):
                col_name = numeric_cols[i]
                try:
                    total = df[col_name].sum()
                    kpi_cols[i].metric(label=f"Total {col_name}", value=f"{total:,.2f}")
                except Exception:
                    kpi_cols[i].metric(label=f"Total {col_name}", value="Error")
        else:
            st.info("No numeric columns found for KPIs.")
    else:
        st.info("No numeric columns found for KPIs.")
    
    st.markdown("---")

    # --- ROW 2: Main Charts (Trend & Pie) ---
    left_col, right_col = st.columns([3, 2]) 

    with left_col:
        # --- Time-Series Chart ---
        if date_col and numeric_cols:
            st.subheader("Trend Analysis")
            
            # Find a good default column (e.g., 'sales', 'amount', or just the first)
            default_trend_col = next((c for c in numeric_cols if 'amount' in c.lower() or 'price' in c.lower()), numeric_cols[0])
            
            sel_num_col = st.selectbox(
                "Select feature for trend:",
                options=numeric_cols,
                index=numeric_cols.index(default_trend_col)
            )
            
            if sel_num_col:
                try:
                    df_sorted = df.dropna(subset=[date_col]).sort_values(by=date_col)
                    
                    if not df_sorted.empty:
                        time_delta = df_sorted[date_col].max() - df_sorted[date_col].min()

                        # Auto-grouping logic
                        if time_delta.days > 365 * 2:
                            period, period_name = 'Y', 'Year'
                        elif time_delta.days > 90:
                            period, period_name = 'M', 'Month'
                        elif time_delta.days > 7:
                            period, period_name = 'W', 'Week'
                        else:
                            period, period_name = 'D', 'Day'
                        
                        st.info(f"💡 Data automatically grouped by **{period_name}**.")

                        # Group and plot
                        df_trend = df.groupby(df[date_col].dt.to_period(period))[sel_num_col].mean().reset_index()
                        df_trend[date_col] = df_trend[date_col].dt.to_timestamp()

                        fig_line = px.line(df_trend, x=date_col, y=sel_num_col, 
                                           title=f"Average {sel_num_col} by {period_name}",
                                           markers=True)
                        st.plotly_chart(fig_line, use_container_width=True)
                    else:
                        st.warning("No valid date data found to plot trend.")
                except Exception as e:
                    st.error(f"Error plotting trend: {e}")
        
        elif cat_cols:
            # --- Fallback: Bar Chart if no date col ---
            st.subheader("Categorical Counts")
            if cat_cols:
                default_bar_col = next((c for c in cat_cols if 1 < df[c].nunique() < 20), cat_cols[0])
                
                bar_choice = st.selectbox(
                    "Select column for Bar Chart:",
                    options=cat_cols,
                    index=cat_cols.index(default_bar_col)
                )
                
                # --- CRASH FIX (Top 15) ---
                try:
                    counts = df[bar_choice].value_counts()
                    if len(counts) > 15:
                        top_n = counts.nlargest(15)
                        other_total = counts.nsmallest(len(counts) - 15).sum()
                        if other_total > 0:
                           top_n['Other'] = other_total
                        final_bar_data = top_n
                    else:
                        final_bar_data = counts
                    
                    final_bar_data = final_bar_data.reset_index()

                    fig_bar = px.bar(final_bar_data, x=bar_choice, y='count',
                                     title=f"Top 15 Counts for '{bar_choice}'")
                    st.plotly_chart(fig_bar, use_container_width=True)
                except Exception as e:
                    st.error(f"Error generating bar chart: {e}")
            else:
                st.info("No categorical columns for bar chart.")
        else:
            st.info("No suitable date or categorical columns to plot here.")

    with right_col:
        # --- Pie Chart ---
        st.subheader("Distribution")
        if cat_cols:
            # Find a good default column for pie (few unique values)
            default_pie_col = next((c for c in cat_cols if 1 < df[c].nunique() < 10), cat_cols[0])
            
            pie_choice = st.selectbox(
                "Select column for Pie Chart:",
                options=cat_cols,
                index=cat_cols.index(default_pie_col)
            )
            
            # --- CRASH FIX (Top 10) ---
            try:
                counts = df[pie_choice].value_counts()
                
                if len(counts) > 10:
                    # Group smallest categories into 'Other'
                    top_n = counts.nlargest(10)
                    other_total = counts.nsmallest(len(counts) - 10).sum()
                    if other_total > 0:
                        top_n['Other'] = other_total
                    final_pie_data = top_n
                else:
                    final_pie_data = counts
                
                st.info("Displaying top 10 values. Others are grouped into 'Other'.")

                fig_pie = px.pie(final_pie_data, names=final_pie_data.index, values=final_pie_data.values,
                                 title=f"Distribution of {pie_choice} (Top 10)")
                fig_pie.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig_pie, use_container_width=True)
            except Exception as e:
                st.error(f"Error generating pie chart: {e}")
        else:
            st.info("No categorical columns for a pie chart.")

    st.markdown("---")
    
    # --- ROW 3: Numeric Analysis (Histogram & Heatmap) ---
    st.subheader("Numeric Feature Analysis")
    
    col1, col2 = st.columns(2)

    with col1:
        # --- Histogram ---
        st.subheader("Histogram")
        if numeric_cols:
            hist_col = st.selectbox("Select feature for Histogram", numeric_cols, index=0)
            try:
                fig_hist = px.histogram(df, x=hist_col, title=f"Distribution of {hist_col}")
                st.plotly_chart(fig_hist, use_container_width=True)
            except Exception as e:
                st.error(f"Error generating histogram: {e}")
        else:
            st.info("No numeric columns for a histogram.")
            
    with col2:
        # --- Correlation Heatmap ---
        st.subheader("Correlation Heatmap")
        if len(numeric_cols) >= 2:
            try:
                corr_matrix = df[numeric_cols].corr(numeric_only=True)
                fig_heatmap = px.imshow(corr_matrix, text_auto=True,
                                        title="Correlation Heatmap",
                                        color_continuous_scale='RdBu_r', # Red-Blue scale
                                        aspect="auto")
                st.plotly_chart(fig_heatmap, use_container_width=True)
            except Exception as e:
                st.error(f"Error generating heatmap: {e}")
        else:
            st.info("Need at least 2 numeric columns for a heatmap.")
            
    st.markdown("---")

    # --- ROW 4: Scatter Plot ---
    if len(numeric_cols) >= 2:
        st.subheader("Relationship Analysis")

        # --- OPTIMIZATION: Only show "safe" columns in the 'color' dropdown ---
        # Find categorical columns suitable for 'color'
        # We limit this to columns with < 20 unique values to prevent crash
        color_opts = [None] # Start with 'None'
        for col in cat_cols:
            unique_count = df[col].nunique()
            # Only add columns that are categorical (more than 1) but not too complex
            if 1 < unique_count < 20:
                color_opts.append(col)
        # --- End of optimization ---
        
        sc_col1, sc_col2, sc_col3 = st.columns(3)
        with sc_col1:
            x_axis = st.selectbox(
                "Select X-axis", 
                numeric_cols, 
                index=0,
                key='scatter_x'
            )
        with sc_col2:
            y_axis = st.selectbox(
                "Select Y-axis", 
                numeric_cols, 
                index=1 if len(numeric_cols) > 1 else 0,
                key='scatter_y'
            )
        with sc_col3:
            # Use the new 'color_opts' list
            color_axis = st.selectbox(
                "Color by (optional)", 
                color_opts, # <-- This is the fix
                help="Only columns with fewer than 20 unique values are shown here.",
                key='scatter_color'
            )

        # Plot the chart
        if x_axis and y_axis:
            try:
                fig_scatter = px.scatter(
                    df, 
                    x=x_axis, 
                    y=y_axis, 
                    color=color_axis,
                    title=f"Relationship between {x_axis} and {y_axis}"
                )
                st.plotly_chart(fig_scatter, use_container_width=True)
            except Exception as e:
                st.error(f"Could not create scatter plot: {e}")
    else:
        st.info("Need at least 2 numeric columns for a scatter plot.")

