from .base import BaseCSVProcess

class ItemDailyFeaturesProcessor(BaseCSVProcess):
    def __init__(self, engine, csv_path):
        super().__init__(engine, csv_path)

    def process(self, table):
        self.df = self.df.loc[self.df.groupby(["video_id"])["date"].idxmax()].reset_index(drop=True)
        super().process(table)
