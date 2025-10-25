import pandas as pd
from typing import List

def generate_insights(df: pd.DataFrame) -> List[str]:
    """
    Generates high-level insights from a given DataFrame.
    """
    insights = []
    
    # Basic dataset info
    insights.append(f"**Dataset Shape:** The dataset contains **{df.shape[0]} rows** and **{df.shape[1]} columns**.")
    
    # Missing values check
    missing_values = df.isnull().sum().sum()
    if missing_values > 0:
        insights.append(f"**Missing Values:** After cleaning, **{missing_values} missing values** still remain.")
    else:
        insights.append(f"**Data Quality:** Great! The dataset has no missing values after cleaning. 👍")
        
    # Column type summary
    numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
    if not numeric_cols.empty:
        insights.append(f"**Numeric Features:** Found **{len(numeric_cols)}** numeric columns.")
        
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns
    if not categorical_cols.empty:
        insights.append(f"**Categorical Features:** Found **{len(categorical_cols)}** categorical columns.")
        
        # Quick Fact
        # Avoid showing 'id' as the most frequent
        valid_cat_cols = [col for col in categorical_cols if 'id' not in col.lower()]
        if valid_cat_cols:
            first_cat_col = valid_cat_cols[0]
            most_frequent = df[first_cat_col].mode()[0]
            insights.append(f"**Quick Fact:** In the **'{first_cat_col}'** column, the most frequent value is **'{most_frequent}'**.")

    return insights

