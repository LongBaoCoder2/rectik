from pathlib import Path
import pandas as pd
from abc import ABC, abstractmethod

from sqlalchemy import Connection

class BaseCSVProcess(ABC):
    def __init__(self, engine: str | Connection, csv_path: str | Path):
        self.engine = engine

        self.csv_path = csv_path
        self.df = pd.read_csv(csv_path, encoding='utf-8-sig', lineterminator='\n')
        self.df = self.df.dropna()

    def process(self, table):
        # Filter DataFrame columns to match the table columns
        db_columns = set(table.columns.keys())
        df_columns = set(self.df.columns)
        valid_columns = list(db_columns & df_columns)

        if not valid_columns:
            print(f"Skipping {self.csv_path}: No matching columns found.")
            return

        # Insert data into the table
        try:
            self.df[valid_columns].to_sql(table.name, self.engine, if_exists='replace', index=False)
            print(f"Successfully ingested {self.csv_path} into {table.name}.")
        except Exception as e:
            print(f"Error inserting {self.csv_path} into {table.name}: {e}")

