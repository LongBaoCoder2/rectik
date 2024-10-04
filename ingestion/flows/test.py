import logging
import os
import pandas as pd
from sqlalchemy import MetaData, create_engine

from utils.table_mapping import TABLE_MAPPING

logging.basicConfig(level=logging.DEBUG)


def start(db_url, data_dir):
        """Start step - initialize database connection and prepare data ingestion"""
        # Create SQLAlchemy engine
        engine = create_engine(db_url)
        # List of CSV files to process
        logging.info(f"Load CSV files in the folder: ${data_dir}")  # Fixed logging issue
        csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
        print(f"Found {len(csv_files)} CSV files: {csv_files}")

        return engine, csv_files

def load_data(data_dir, engine, csv_files):
    """Load data from CSV files into PostgreSQL"""
    # Create metadata object to reflect database schema
    metadata = MetaData()  # Removed bind here
    metadata.reflect(bind=engine)  # Passed bind to reflect() method

    # Loop over each CSV file and process
    for csv_file in csv_files:
        table_name = os.path.splitext(csv_file)[0]
        table_name = TABLE_MAPPING.get(table_name, None)
        csv_path = os.path.join(data_dir, csv_file)

        # Check if table exists in the database
        if table_name is not None and table_name in metadata.tables:
            table = metadata.tables[table_name]
            ingest_csv_to_table(engine, csv_path, table)
        else:
            print(f"Skipping {csv_file}: No matching table found in the database.")


def ingest_csv_to_table(engine, csv_path, table):
    """Read CSV and insert into the specified table, ignoring missing columns"""
    # Read CSV into DataFrame
    df = pd.read_csv(csv_path, encoding='utf-8-sig', lineterminator='\n')

    # Filter DataFrame columns to match the table columns
    db_columns = set(table.columns.keys())
    df_columns = set(df.columns)
    valid_columns = list(db_columns & df_columns)

    if not valid_columns:
        print(f"Skipping {csv_path}: No matching columns found.")
        return

    # Insert data into the table
    try:
        df[valid_columns].to_sql(table.name, engine, if_exists='replace', index=False)
        print(f"Successfully ingested {csv_path} into {table.name}.")
    except Exception as e:
        print(f"Error inserting {csv_path} into {table.name}: {e}")



def main():
    db_url = "postgresql://postgres:sau28@localhost/recommender"
        
    data_dir = os.getenv("DATA_DIR", "./data/KuaiRec 2.0/data")

    print("Starting")
    engine, csv_files = start(db_url, data_dir)
    load_data(data_dir, engine, csv_files)

    print("Data ingestion completed successfully.")

if __name__ == "__main__":
    main()