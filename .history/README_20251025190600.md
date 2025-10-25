🚀 Advanced Data Pipeline & Dashboard Generator

This is an advanced data project that demonstrates a complete workflow for processing massive datasets (GB-scale) with PySpark and visualizing them in a high-performance, interactive dashboard using Streamlit.

This project solves the most common problem with data dashboards: it can handle files that are too large to fit in memory, preventing the app crashes (due to RAM overflow) that happen with standard tools like pandas.read_csv.

The 2-Part Professional Workflow

This project is built using a two-part pipeline, separating heavy processing from fast visualization.

1. The "Processor" (app1/)

Technology: PySpark

Job: This script handles the heavy lifting. It reads a massive, raw data file (e.g., a 2GB .parquet file), cleans it at scale, extracts a representative random sample (e.g., 100,000 rows), and saves it as a small, clean CSV file (cleaned_sample.csv).

2. The "Visualizer" (app/)

Technology: Streamlit, Pandas, Plotly

Job: This is the interactive web app. It loads the small, pre-processed cleaned_sample.csv file, providing a fast, crash-proof dashboard with a full suite of charts (KPIs, Trends, Heatmaps, etc.).

📊 Key Features & Improvements

Scalability: The PySpark processor can handle datasets of virtually any size (GBs or TBs).

Performance: The Streamlit dashboard is extremely fast because it only loads the small, pre-processed sample.

Robustness: Charts are crash-proof. Pie/Bar charts automatically group small categories (Top 10/15 logic) to prevent memory crashes.

Flexibility: The Streamlit app (app/) is also a powerful standalone tool! You can skip the Spark processor and use it to upload and analyze any small CSV, JSON, or Excel file directly.

How to Use

Part 1: The Big Data Workflow (For GB-scale files)

Prerequisites: Install Java JDK 11 (required for PySpark).

Setup Environment:

Note: A virtual environment (venv) is highly recommended to manage project dependencies and avoid conflicts with other Python projects. However, if you prefer, you can skip this step and install the packages globally (system-wide) in the next step.

# Create a virtual environment
python -m venv venv
# Activate it
source venv/bin/activate


Install Dependencies:

# Install processor & app requirements
pip install -r app1/requirements_processing.txt
pip install -r app/requirements_app.txt


Place Data: Copy your large raw file (e.g., yellow_tripdata_2017-01.parquet) into the data/raw/ directory.

Configure & Run Processor:

Open app1/process_data.py and update RAW_FILE_PATH (Line 11) to your file's name.

(If not .parquet) Update the spark.read function (Line 41).

Run the script:

python app1/process_data.py


Wait for it to create cleaned_sample.csv in data/processed/.

Run the Dashboard:

streamlit run app/app.py


Visualize: In the browser, upload the new data/processed/cleaned_sample.csv file.

Part 2: The Small File Workflow

Use this for any regular CSV, JSON, or Excel file.

Skip Part 1 (no Spark needed).

Run the Dashboard:

streamlit run app/app.py


Visualize: Upload your small file directly.

Technology Stack

Data Processing: PySpark

Dashboard UI: Streamlit

Data Manipulation: Pandas

Visualization: Plotly Express