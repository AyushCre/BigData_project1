🚀 Advanced Data Pipeline & Dashboard Generator | PySpark + Streamlit + Plotly  

Developed a scalable, end‑to‑end big data pipeline that processes GB‑scale datasets using PySpark and visualizes them in a high‑performance, interactive Streamlit dashboard. This solution overcomes memory overflow issues by separating heavy data processing from fast, crash‑proof visualization.

⚙️ 2‑Part Workflow  
• **Processor (app1/):** PySpark cleans and processes large raw data files (e.g., 2GB .parquet), extracts a representative 100K‑row sample, and saves it as `cleaned_sample.csv`.  
• **Visualizer (app/):** Streamlit, Plotly, and Pandas power the dashboard to explore aggregated data interactively via KPIs, trends, and heatmaps.

📊 Key Highlights  
• **Scalability:** Distributed PySpark handles multi‑GB/TB datasets.  
• **Performance:** Streamlit dashboards load instantly from small samples.  
• **Robustness:** Top‑10/15 grouping logic avoids memory overflow.  
• **Flexibility:** Can also load small CSV/Excel/JSON data directly without Spark.

💻 **Setup & Commands**

👉 [Create and activate virtual environment](python -m venv venv && source venv/bin/activate)  

👉 [Install dependencies](pip install -r app1/requirements_processing.txt && pip install -r app/requirements_app.txt)  

👉 [Place your data file](data/raw/)  

👉 [Edit configuration paths](app1/process_data.py — Line 11: RAW_FILE_PATH, Line 41: spark.read)  

👉 [Run the PySpark processor](python app1/process_data.py)  

👉 [Launch the Streamlit dashboard](streamlit run app/app.py)  

👉 [Upload the processed file](data/processed/cleaned_sample.csv)

🧠 **Tech Stack:** PySpark | Streamlit | Plotly | Pandas | Python  

For a detailed explanation and demo video, please visit my GitHub repository.  
To explore the entire codebase and workflow, check it out on my GitHub profile.
