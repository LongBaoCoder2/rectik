from metaflow import FlowSpec, step, Parameter
from sqlalchemy import create_engine, MetaData
import os
import logging
from process.base import BaseCSVProcess
from process.item_daily_features import ItemDailyFeaturesProcessor
from utils import TABLE_MAPPING

logging.basicConfig(level=logging.DEBUG)

class DataIngestionFlow(FlowSpec):
    db_url = Parameter(
        "db_url",
        help="Database URL for PostgreSQL",
        default=os.getenv("DB_URL", "postgresql://postgres:sau28@postgres/recommender")
    )
    data_dir = Parameter(
        "data_dir",
        help="Directory path containing CSV files",
        default=os.getenv("DATA_DIR", "/app/data")
    )

    @step
    def start(self):
        """Start step - initialize database connection and prepare data ingestion"""
        logging.info(f"Load CSV files in the folder: ${self.data_dir}")
        self.csv_files = [f for f in os.listdir(self.data_dir) if f.endswith('.csv')]
        print(f"Found {len(self.csv_files)} CSV files: {self.csv_files}")
        self.next(self.load_data)

    @step
    def load_data(self):
        """Load data from CSV files into PostgreSQL"""
        engine = create_engine(self.db_url)
        metadata = MetaData()
        metadata.reflect(bind=engine)
        for csv_file in self.csv_files:
            table_names = os.path.splitext(csv_file)[0]
            table_names = TABLE_MAPPING.get(table_names, None)
            csv_path = os.path.join(self.data_dir, csv_file)

            if table_names is None:
                print(f"Skipping {csv_file}: No matching table found in the database.")
                continue

            for table_name in table_names:
                if table_name in metadata.tables:
                    table = metadata.tables[table_name]
                    self.ingest_csv_to_table(engine, csv_path, table)
                else:
                    print(f"Skipping {csv_file}: No matching table found in the database.")

        self.next(self.end)

    def ingest_csv_to_table(self, engine, csv_path, table):
        """Read CSV and insert into the specified table, ignoring missing columns"""
        if "item_daily_features" in csv_path:
            processor = ItemDailyFeaturesProcessor(engine=engine, csv_path=csv_path)
        else:
            processor = BaseCSVProcess(engine=engine, csv_path=csv_path)
        processor.process(table)

    @step
    def end(self):
        """End of the workflow"""
        print("Data ingestion completed successfully.")

if __name__ == '__main__':
    DataIngestionFlow()

# import os
# import logging

# from process.base import BaseCSVProcess
# from process.item_daily_features import ItemDailyFeaturesProcessor

# from utils import TABLE_MAPPING

# logging.basicConfig(level=logging.DEBUG)

# class DataIngestionFlow(FlowSpec):
    
#     # Parameters to configure database connection and data paths
    
#     db_url = Parameter(
#         "db_url",
#         help="Database URL for PostgreSQL",
#         default=os.getenv("DB_URL", "postgresql://postgres:sau28@postgres/recommender")
#     )
#     data_dir = Parameter(
#         "data_dir",
#         help="Directory path containing CSV files",
#         default=os.getenv("DATA_DIR", "/app/data")
#     )

#     @step
#     def start(self):
#         """Start step - initialize database connection and prepare data ingestion"""
#         # Create SQLAlchemy engine
#         self.engine = create_engine(self.db_url)
#         # List of CSV files to process
#         logging.info(f"Load CSV files in the folder: ${self.data_dir}")  # Fixed logging issue
#         self.csv_files = [f for f in os.listdir(self.data_dir) if f.endswith('.csv')]
#         print(f"Found {len(self.csv_files)} CSV files: {self.csv_files}")
#         self.next(self.load_data)

#     @step
#     def load_data(self):
#         """Load data from CSV files into PostgreSQL"""
#         # Create metadata object to reflect database schema
#         metadata = MetaData()  # Removed bind here
#         metadata.reflect(bind=self.engine)  # Passed bind to reflect() method

#         # Loop over each CSV file and process
#         for csv_file in self.csv_files:
#             table_name = os.path.splitext(csv_file)[0]
#             table_name = TABLE_MAPPING.get(table_name, None)
#             csv_path = os.path.join(self.data_dir, csv_file)

#             # Check if table exists in the database
#             if table_name is not None and table_name in metadata.tables:
#                 table = metadata.tables[table_name]
#                 self.ingest_csv_to_table(csv_path, table)
#             else:
#                 print(f"Skipping {csv_file}: No matching table found in the database.")
        
#         self.next(self.end)

#     def ingest_csv_to_table(self, csv_path, table):
#         """Read CSV and insert into the specified table, ignoring missing columns"""
#         # Read CSV into DataFrame
#         if "item_daily_features" in csv_path:
#             processor = ItemDailyFeaturesProcessor(engine=self.engine, csv_path=csv_path)
#         else:
#             processor = BaseCSVProcess(engine=self.engine, csv_path=csv_path)

#         processor.process(table)
        


#     @step
#     def end(self):
#         """End of the workflow"""
#         print("Data ingestion completed successfully.")

# if __name__ == '__main__':
#     DataIngestionFlow()
