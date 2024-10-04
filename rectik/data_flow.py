from metaflow import FlowSpec, step, batch, Parameter, current
from datetime import datetime
from decorators import magicdir

class DataPrepareFlow(FlowSpec):
    
    # Parameter: Row sampling percentage (1 to 100); 0 means no sampling.
    ROW_SAMPLING = Parameter(
        name='row_sampling',
        help='Row sampling: if 0, NO sampling is applied. Needs to be an int between 1 and 100',
        default='1'
    )

    # Parameter: Directory where the processed datasets will be stored.
    PROCESSED_DATA_DIR = Parameter(
        name="processed_data_dir",
        help="Directory storing the processed data. This will have train test dataset for training flow.",
        default="/rectik/data/processed"
    )

    # Parameter: Path to the user dataset file (parquet format).
    USER_DATASET_PATH = Parameter(
        name="user_dataset_path",
        help="Path to user parquet file.",
        default="/rectik/data/user.parquet"
    )

    # Parameter: Path to the video dataset file (parquet format).
    VIDEO_DATASET_PATH = Parameter(
        name="video_dataset_path",
        help="Path to video parquet file.",
        default="/rectik/data/video.parquet"
    )

    # Parameter: Path to the user-item interaction dataset file (parquet format).
    USER_VIDEO_DATASET_PATH = Parameter(
        name="user_video_dataset_path",
        help="Path to video parquet file.",
        default="/rectik/data/user_item.parquet"
    )

    # Parameter: Date up to which data is used for training (yyyy-mm-dd format).
    TRAINING_END_DATE = Parameter(
        name='training_end_date',
        help='Data up until this date is used for training, format yyyy-mm-dd',
        default='2020-08-28'
    )

    # Parameter: Date up to which data is used for validation (yyyy-mm-dd format).
    VALIDATION_END_DATE = Parameter(
        name='validation_end_date',
        help='Data up until this date is used for validation, format yyyy-mm-dd',
        default='2020-09-03'
    )

    FEATURE_REPO_PATH = Parameter(
        name="feature_repo_path",
        help="The feature store repository directory.",
        default="/rectik/feast_repo/feature_repo"
    )


    @step
    def start(self):
        """
        Initial step of the flow to validate parameters and configuration.
        Validates date ranges and checks whether Metaflow is using local or remote storage.
        """
        import os

        # Log the flow start information
        print(f"Starting the flow: {current.flow_name} | Run ID: {current.run_id} | User: {current.username}")
        
        # Check if Metaflow is using a remote S3 data store or local storage
        from metaflow.metaflow_config import DATASTORE_SYSROOT_S3 
        if DATASTORE_SYSROOT_S3:
            print("Using remote data store: S3")
        else:
            print("Local data store enabled")

        
        if os.path.isdir(self.FEATURE_REPO_PATH):
            print(f"Feature store reposity working path: {self.FEATURE_REPO_PATH}")
        else:
            print(f"WARNING: feature store path is not found. The flow might might work unexpectedly")

        # Log the row sampling parameter
        print(f"Row Sampling: {self.ROW_SAMPLING}%")

        # Validate the training and validation date ranges
        self.training_end_date = datetime.strptime(self.TRAINING_END_DATE, '%Y-%m-%d')
        self.validation_end_date = datetime.strptime(self.VALIDATION_END_DATE, '%Y-%m-%d')
        assert self.validation_end_date > self.training_end_date, "Validation date must be later than training date"
        print(f"Training End Date: {self.TRAINING_END_DATE} | Validation End Date: {self.VALIDATION_END_DATE}")
        
        # Proceed to the next step to fetch the user dataset
        self.next(self.get_user_dataset)

    @step
    def get_user_dataset(self):
        """
        Fetch the user dataset using DuckDB and log the result.
        Runs a query defined by USER_FEATURE_QUERY.
        """
        import os
        import duckdb
        from query_string import USER_FEATURE_QUERY

        # Format the query string and execute it
        query = USER_FEATURE_QUERY.format(self.USER_DATASET_PATH, "")
        print(f"Fetching user dataset with query:\n{query}")

        con = duckdb.connect(database=':memory:')
        self.user_df = con.execute(query).df()

        # Log the number of rows fetched and display a sample
        print(f"Fetched {len(self.user_df)} rows from user dataset.")    

        # Proceed to the next step to fetch the video dataset
        self.next(self.get_video_dataset)

    @step
    def get_video_dataset(self):
        """
        Fetch the video dataset using DuckDB and log the result.
        Runs a query defined by VIDEO_FEATURES_QUERY.
        """
        import os
        import duckdb
        from query_string import VIDEO_FEATURES_QUERY

        # Format and execute the query for fetching video data
        query = VIDEO_FEATURES_QUERY.format(self.VIDEO_DATASET_PATH, "")
        print(f"Fetching video dataset with query:\n{query}")

        con = duckdb.connect(database=':memory:')
        self.video_df = con.execute(query).df()

        # Log the number of rows fetched and display a sample
        print(f"Fetched {len(self.video_df)} rows from video dataset.")
    

        # Proceed to the next step to fetch the user-video interaction dataset
        self.next(self.get_user_video_dataset)

    @step
    def get_user_video_dataset(self):
        """
        Fetch the user-item interaction dataset, applying sampling if specified.
        Runs a query defined by USER_ITEM_INTERACTION_QUERY.
        """
        import duckdb
        from query_string import USER_ITEM_INTERACTION_QUERY

        # Apply sampling if ROW_SAMPLING is non-zero
        _sampling = int(self.ROW_SAMPLING)
        sampling_expression = '' if _sampling == 0 else f'USING SAMPLE {_sampling} PERCENT (bernoulli)'

        query = USER_ITEM_INTERACTION_QUERY.format(self.USER_VIDEO_DATASET_PATH, sampling_expression)
        print(f"Fetching user-item interaction dataset with query:\n{query}")

        con = duckdb.connect(database=':memory:')
        self.user_video_df = con.execute(query).df()

        # Log the number of rows fetched and display a sample
        print(f"Fetched {len(self.user_video_df)} rows from user-item interaction dataset.")
        print(self.user_video_df.head())

        # Proceed to the next step to split the datasets for training, testing, and validation
        self.next(self.train_test_split)

    @magicdir
    @step 
    def train_test_split(self):
        """
        Split the user-item interaction dataset into train, test, and validation sets based on interaction date.
        Converts dates to datetime objects for filtering.
        """        
        import pandas as pd
        from merlin.io import Dataset

        # Ensure the interaction_date column is in datetime format for filtering
        self.user_video_df['interaction_date'] = pd.to_datetime(self.user_video_df['interaction_date'])
        
        # Split data based on interaction_date for training, testing, and validation
        self.train_df = self.user_video_df[self.user_video_df['interaction_date'] < self.training_end_date]
        self.test_df = self.user_video_df[
            (self.user_video_df['interaction_date'] >= self.training_end_date) &
            (self.user_video_df['interaction_date'] < self.validation_end_date)
        ]
        self.valid_df = self.user_video_df[self.user_video_df['interaction_date'] >= self.validation_end_date]

        # Convert user and video datasets to Merlin Dataset format
        self.user_dataset = Dataset(self.user_df)
        self.video_dataset = Dataset(self.video_df)

        # Proceed to the next step to merge the datasets
        self.next(self.merge_train_dataset)

    @step
    def merge_train_dataset(self):
        """
        Merge the training dataset with user and video features based on user_id and video_id.
        """
        from merlin.io import Dataset

        print("User dataframe columns: ", self.user_df.columns)
        print("Video dataframe columns: ", self.video_df.columns)

        print("Merging datasets for training...")

        # Convert the train dataset into Merlin's Dataset format
        train_dataset = Dataset(self.train_df)

        # Merge user and video features into the training dataset
        train_dataset = Dataset.merge(train_dataset, self.user_dataset, on='user_id', how='left')
        train_dataset = Dataset.merge(train_dataset, self.video_dataset, on='video_id', how='left')

        # Log the result of the merge
        print(f"Merged dataset with {train_dataset.num_rows} rows.")
        print(f"Example head: ", train_dataset.head())
        self.train_dataset = train_dataset

        # Proceed to the next step to merge the test datasets
        self.next(self.merge_test_dataset)

    @step
    def merge_test_dataset(self):
        """
        Merge the test dataset with user and video features based on user_id and video_id.
        """
        from merlin.io import Dataset

        print("Merging datasets for testing...")

        # Convert the test dataset into Merlin's Dataset format
        test_dataset = Dataset(self.test_df)

        # Merge user and video features into the test dataset
        test_dataset = Dataset.merge(test_dataset, self.user_dataset, on='user_id', how='left')
        test_dataset = Dataset.merge(test_dataset, self.video_dataset, on='video_id', how='left')

        # Log the result of the merge
        print(f"Merged dataset with {test_dataset.num_rows} rows.")
        print(f"Example head: ", test_dataset.head())
        self.test_dataset = test_dataset

        # Proceed to the next step to merge the validation datasets
        self.next(self.merge_valid_dataset)

    @step
    def merge_valid_dataset(self):
        """
        Merge the validation dataset with user and video features based on user_id and video_id.
        """
        from merlin.io import Dataset

        print("Merging datasets for validation...")

        # Convert the validation dataset into Merlin's Dataset format
        valid_dataset = Dataset(self.valid_df)

        # Merge user and video features into the validation dataset
        valid_dataset = Dataset.merge(valid_dataset, self.user_dataset, on='user_id', how='left')
        valid_dataset = Dataset.merge(valid_dataset, self.video_dataset, on='video_id', how='left')

        # Log the result of the merge
        print(f"Merged dataset with {valid_dataset.num_rows} rows.")
        print(f"Example head: ", valid_dataset.head())
        self.valid_dataset = valid_dataset

        # Proceed to the final step to save the processed datasets
        self.next(self.build_workflow)


    @step
    def build_workflow(self):
        """
        Build the NVTabular workflow by combining user, video, and interaction workflows
        """
        from nvtabular import ops
        from workflows import outputs

        print("Building NVTabular workflow...")
        self.workflow = (interaction_workflow + user_workflow + video_workflow) >> ops.Dropna()

        self.next(self.fit_train_workflow)


    @magicdir
    @step
    def fit_train_workflow(self):
        """
        Fit the NVTabular workflow and transform the data
        """
        import os
        import nvtabular as nvt

        print("Fitting the workflow on train dataset...")
        self.fitted_workflow = nvt.Workflow(self.workflow).fit(self.train_dataset)
        self.fitted_workflow.save(os.path.join(self.PROCESSED_DATA_DIR, "workflow"))

        # Log the result of the transformation
        print(f"Succesfully fit the workflow on train dataset.")

        self.next(self.transform_train_workflow)

    @magicdir
    @step
    def transform_train_workflow(self):
        """
        Transform the NVTabular workflow 
        """
        import os

        print("Transforming the workflow on train dataset...")
        self.train_features = self.fitted_workflow.transform(self.train_dataset)
        self.train_features.to_parquet(
                os.path.join(self.PROCESSED_DATA_DIR, "train")
        )

        print("Schema: ", self.train_features.to_ddf().dtypes)

        # Log the result of the transformation
        print(f"Data transformed and saved to parquet. ")

        self.next(self.transform_test_workflow)


    @magicdir
    @step
    def transform_test_workflow(self):
        """
        Transform the NVTabular workflow 
        """
        import os

        print("Transforming the workflow on test dataset...")
        self.fitted_workflow.transform(self.train_dataset).to_parquet(
                os.path.join(self.PROCESSED_DATA_DIR, "test")
        )

        # Log the result of the transformation
        print(f"Data transformed and saved to parquet. ")

        self.next(self.transform_valid_workflow)


    @magicdir
    @step
    def transform_valid_workflow(self):
        """
        Fit the NVTabular workflow and transform the data
        """
        import os

        print("Transforming the workflow on valid dataset...")
        self.fitted_workflow.transform(self.train_dataset).to_parquet(
                os.path.join(self.PROCESSED_DATA_DIR, "valid")
        )

        # Log the result of the transformation
        print(f"Data transformed and saved to parquet. ")

        self.next(self.extract_user_item_features)

    @magicdir
    @step
    def extract_user_item_features(self):
        """
        Extract user item features from transformed train dataset.
        """
        import os
        from merlin.schema.tags import Tags
        from merlin.models.utils.dataset import unique_rows_by_features

        print("Extracting user features...")
        
        user_features = (
            unique_rows_by_features(self.train_features, Tags.USER, Tags.USER_ID)
            .compute()
            .reset_index(drop=True)
        )

        user_features["datetime"] = datetime.now()
        user_features["datetime"] = user_features["datetime"].astype("datetime64[ns]")
        user_features["created"] = datetime.now()
        user_features["created"] = user_features["created"].astype("datetime64[ns]")

        user_features_path = os.path.join(self.FEATURE_REPO_PATH, "data", "user_features.parquet")
        user_features.to_parquet(user_features_path)
        print(f"User features saved to {user_features_path}")
        
        # Extract unique item features
        video_features = (
            unique_rows_by_features(self.train_features, Tags.ITEM, Tags.ITEM_ID)
            .compute()
            .reset_index(drop=True)
        )

        video_features["datetime"] = datetime.now()
        video_features["datetime"] = video_features["datetime"].astype("datetime64[ns]")
        video_features["created"] = datetime.now()
        video_features["created"] = video_features["created"].astype("datetime64[ns]")

        video_df_path = os.path.join(self.FEATURE_REPO_PATH, "data", "video_features.parquet")
        video_features.to_parquet(video_df_path)
        print("Video Features stored at the path: ", video_df_path)

        # Log the result of the transformation
        self.next(self.end)


    @magicdir
    @step
    def end(self):
        """
        End of the flow
        """
        print("Flow streaming. Happy for it.")

if __name__ == "__main__":
    DataPrepareFlow()
