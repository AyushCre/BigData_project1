import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, regexp_replace, trim

# --- Configuration ---
# TODO: Update the path to your raw file here
RAW_FILE_PATH = "../data/raw/your_5gb_file.csv"

# Where to save the new sample file
OUTPUT_FILE_PATH = "../data/processed/cleaned_sample.csv"

# How many rows do you want in the sample (e.g., 100,000)
# These will be randomly selected from the entire 5GB file
SAMPLE_SIZE = 100000 
# --- End Configuration ---


def main():
    print("PySpark Data Processor script starting...")
    
    # 1. Create SparkSession
    # This will start the Spark engine on your system
    try:
        spark = SparkSession.builder \
            .appName("BigDataCleanerAndSampler") \
            .master("local[*]") \
            .config("spark.driver.memory", "4g") \
            .getOrCreate()
    except Exception as e:
        print("Error: SparkSession could not be started.")
        print("Have you installed Java JDK 11?")
        print(f"Details: {e}")
        return

    print(f"SparkSession started. Reading {RAW_FILE_PATH}...")

    # 2. Read the 5GB Raw File
    try:
        df = spark.read.csv(RAW_FILE_PATH, header=True, inferSchema=False)
    except Exception as e:
        print(f"Error: File {RAW_FILE_PATH} not found or could not be read.")
        print(f"Details: {e}")
        spark.stop()
        return

    # 3. Clean the Data using Spark
    # (Assuming you have 'actual_price', 'selling_price', 'average_rating' columns)
    # This will remove '$', '₹', ',' and extra whitespace from those columns
    print("Starting data cleaning...")
    try:
        df_cleaned = df \
            .withColumn("actual_price", regexp_replace(col("actual_price"), "[$,₹,]", "")) \
            .withColumn("selling_price", regexp_replace(col("selling_price"), "[$,₹,]", "")) \
            .withColumn("actual_price", trim(col("actual_price")).cast("double")) \
            .withColumn("selling_price", trim(col("selling_price")).cast("double")) \
            .withColumn("average_rating", trim(col("average_rating")).cast("double"))
        
        # Drop rows where price could not be cleaned (became null)
        df_cleaned = df_cleaned.dropna(subset=["actual_price", "selling_price", "average_rating"])
        
        print("Data cleaning complete.")
    except Exception as e:
        print("Error: An error occurred during cleaning. Check if column names are correct.")
        print(f"Details: {e}")
        spark.stop()
        return

    # 4. Take a Random Sample from the full dataset
    print(f"Taking a random sample of {SAMPLE_SIZE} rows...")
    
    total_rows = df_cleaned.count()
    if total_rows == 0:
        print("Error: No data left after cleaning.")
        spark.stop()
        return

    # Calculate fraction needed for sampling
    fraction = min(1.0, (SAMPLE_SIZE * 1.2) / total_rows) # A bit extra to get approx size
    
    df_sample = df_cleaned.sample(withReplacement=False, fraction=fraction).limit(SAMPLE_SIZE)

    # 5. Save the small Sample File
    print(f"Saving sample to {OUTPUT_FILE_PATH}...")
    
    # Spark saves as a folder by default. Convert to Pandas to save as a single CSV file.
    try:
        # Warning: Ensure the sample is not too large to fit in the driver's memory (e.g., 4g)
        pandas_df = df_sample.toPandas()
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(OUTPUT_FILE_PATH), exist_ok=True)
        
        pandas_df.to_csv(OUTPUT_FILE_PATH, index=False)
        
        print("-" * 30)
        print("SUCCESS!")
        print(f"New file saved here: {OUTPUT_FILE_PATH}")
        print(f"Now, go to '2_dashboard_app', run Streamlit, and upload this new file.")
        print("-" * 30)

    except Exception as e:
        print(f"Error: Could not save sample file.")
        print(f"Details: {e}")

    # 6. Stop the Spark session
    spark.stop()

if __name__ == "__main__":
    main()

