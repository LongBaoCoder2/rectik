from metaflow import FlowSpec, Parameter, step, current

class TrainingFlow(FlowSpec):

    # Parameters
    PROCESSED_DATA_DIR = Parameter(
        name="processed_data_dir",
        help="Directory storing the processed data. This will have train, test, and valid datasets for training flow.",
        default="/rectik/data/processed"
    )

    SAVE_DIR = Parameter(
        name="save_dir",
        help="Directory to save model artifacts",
        default="/rectik/artifacts"
    )

    PART_SIZE = Parameter(
        name="part_size",
        help="Fraction of the dataset to use for training (including test & validation)",
        default=None,
    )

    VIDEO_FEATURES_FILE = Parameter(
        name="video_features_file",
        help="Path to the file storing video features",
        default="/rectik/feast_repo/feature_repo/data/video_features.parquet"
    )

    TOP_K = Parameter(
        name="top_k",
        help="Metrics At K (NDCG@K, Recall@K)",
        default="10"
    )

    BATCH_SIZE = Parameter(
        name="batch_size",
        help="Training batch size.",
        default="1024"
    )

    EPOCHS = Parameter(
        name="epochs",
        help="training epochs",
        default="5"
    )

    EMBEDDING_DIM = Parameter(
        name="embedding_dim",
        help="dimension of embedding space.",
        default="64"
    )

    @step
    def start(self):
        """
        Start-up: validate parameters and initialize the flow.
        """
        import os

        # Log start of the flow
        print(f"Starting the flow: {current.flow_name} | Run ID: {current.run_id} | User: {current.username}")
        
        # Check if Metaflow is using remote (S3) data store or local
        from metaflow.metaflow_config import DATASTORE_SYSROOT_S3 
        if DATASTORE_SYSROOT_S3:
            print("Using remote data store: S3")
        else:
            print("Local data store enabled")

        # Validate processed data directory
        if not os.path.isdir(self.PROCESSED_DATA_DIR):
            raise ValueError(f"PROCESSED_DATA_DIR not found. Please provide a valid path: {self.PROCESSED_DATA_DIR}")

        # Validate save directory
        if not os.path.isdir(self.SAVE_DIR):
            raise ValueError(f"SAVE_DIR not found. Please provide a valid directory: {self.SAVE_DIR}")
        
        # Validate top k
        self.top_k = int(self.TOP_K)
        if not (self.top_k >= 0):
            raise ValueError(f"Invalid TOP_K. It must be not negative. Provided: {self.top_k}")
    
        # Validate batch size
        self.batch_size = int(self.BATCH_SIZE)
        if not (self.batch_size >= 0):
            raise ValueError(f"Invalid BATCH_SIZE. It must be not negative. Provided: {self.batch_size}")
        
        # Validate epochs
        self.epochs = int(self.EPOCHS)
        if not (self.epochs >= 0):
            raise ValueError(f"Invalid EPOCHS. It must be not negative. Provided: {self.epochs}")

        self.embedding_dim = int(self.EMBEDDING_DIM)
        if not (self.embedding_dim >= 0):
            raise ValueError(f"Invalid EMBEDDING_DIM. It must be not negative. Provided: {self.epochs}")


        self.train_data_path = os.path.join(self.PROCESSED_DATA_DIR, "train")
        self.test_data_path = os.path.join(self.PROCESSED_DATA_DIR, "test")
        self.valid_data_path = os.path.join(self.PROCESSED_DATA_DIR, "valid")

        print(f"Validated paths:\nTrain: {self.train_data_path}\nTest: {self.test_data_path}\nValid: {self.valid_data_path}")
        
        # Proceed to the next step
        self.next(self.train_twotower_model)


    @step
    def train_twotower_model(self):
        """
        Train the TwoTower model and log the process.
        """
        import os

        import nvtabular as nvt
        import merlin.models.tf as mm
        from merlin.io import Dataset
        from merlin.systems.dag.ops.tensorflow import PredictTensorflow
        from merlin.systems.dag.ops.workflow import TransformWorkflow

        from workflows import outputs
        from constant import VIDEO_FEATURE_LIST

        # Load datasets
        print(f"Loading training data from {self.train_data_path}...")
        train_data = Dataset(f"{self.train_data_path}/*.parquet", part_size=self.PART_SIZE)
        
        print(f"Loading test data from {self.test_data_path}...")
        test_data = Dataset(f"{self.test_data_path}/*.parquet", part_size=self.PART_SIZE)
        
        print(f"Loading validation data from {self.valid_data_path}...")
        valid_data = Dataset(f"{self.valid_data_path}/*.parquet", part_size=self.PART_SIZE)

        # Load schema for retrieval task
        print("Loading schema for the retrieval task...")
        schema = self.load_schema('retrieval', train_data)
        
        train_data.schema = schema
        test_data.schema = schema
        valid_data.schema = schema

        # Initialize TwoTower model
        print("Initializing the TwoTower model...")
        self.model_tt = mm.TwoTowerModel(
            schema,
            query_tower=mm.MLPBlock([128, self.embedding_dim], no_activation_last_layer=True),
            samplers=[mm.InBatchSampler()],
            embedding_options=mm.EmbeddingOptions(infer_embedding_sizes=True),
        )

        # Compile the model
        print("Compiling the TwoTower model...")
        self.model_tt.compile(
            optimizer="adam",
            run_eagerly=False,
            metrics=[mm.RecallAt(self.top_k), mm.NDCGAt(self.top_k)],
        )

        # Train the model
        print("Starting to train the TwoTower model...")
        self.model_tt.fit(train_data, 
                          validation_data=valid_data, 
                          batch_size=self.batch_size, 
                          epochs=self.epochs)
        
        print("Training completed for TwoTower model.")

        # Save the query tower part of the model
        print(f"Saving the query tower to {self.SAVE_DIR}/query_tower...")
        query_tower = self.model_tt.retrieval_block.query_block()
        query_tower.save(f"{self.SAVE_DIR}/query_tower")
        print(f"Query tower saved successfully to {self.SAVE_DIR}/query_tower")

        # Set up workflow for item embeddings
        train_data_path = os.path.join(self.PROCESSED_DATA_DIR, "train")
        train_data = Dataset(f"{train_data_path}/*.parquet")
        nvt_wkflow = nvt.Workflow(outputs)
        nvt_wkflow.fit(train_data)

        video_features = Dataset(self.VIDEO_FEATURES_FILE)
        video_embedding_workflow = nvt.Workflow(["video_id"] + ((['video_id'] + VIDEO_FEATURE_LIST) 
                                                >> TransformWorkflow(nvt_wkflow.get_subworkflow("video")) 
                                                >> PredictTensorflow(self.model_tt.first.item_block())))
        video_embeddings = video_embedding_workflow.fit_transform(video_features).to_ddf().compute()
        video_embeddings.to_parquet(os.path.join(self.SAVE_DIR, "video_embeddings.parquet"))


        # Proceed to train the DLRM model
        self.next(self.train_dlrm)

    @step
    def train_dlrm(self):
        """
        Train the DLRM model and log the process.
        """
        import tensorflow as tf
        import merlin.models.tf as mm
        from merlin.io import Dataset
        from merlin.schema.tags import Tags

        # Load datasets
        print(f"Loading training data from {self.train_data_path}...")
        train_data = Dataset(f"{self.train_data_path}/*.parquet", part_size=self.PART_SIZE)
        
        print(f"Loading test data from {self.test_data_path}...")
        test_data = Dataset(f"{self.test_data_path}/*.parquet", part_size=self.PART_SIZE)
        
        print(f"Loading validation data from {self.valid_data_path}...")
        valid_data = Dataset(f"{self.valid_data_path}/*.parquet", part_size=self.PART_SIZE)

        # Load schema for DLRM task
        print("Loading schema for the DLRM task...")
        schema = self.load_schema('dlrm', train_data)

        # Select the target column
        target_column = schema.select_by_tag(Tags.TARGET).column_names[0]
        print(f"Target column identified for the DLRM model: {target_column}")

        # Initialize DLRM model
        print("Initializing the DLRM model...")
        model = mm.DLRMModel(
            schema,
            embedding_dim=self.embedding_dim,
            bottom_block=mm.MLPBlock([128, 64]),
            top_block=mm.MLPBlock([128, 64, 32]),
            prediction_tasks=mm.RegressionTask(target_column),
        )

        # Compile the model
        print("Compiling the DLRM model...")
        model.compile(optimizer="adam", run_eagerly=False, metrics=[tf.keras.metrics.AUC()])

        # Train the model
        print("Starting to train the DLRM model...")
        model.fit(train_data, validation_data=valid_data, batch_size=32)
        
        print("Training completed for DLRM model.")
        self.model_dlrm = model

        # Save the DLRM model
        print(f"Saving the DLRM model to {self.SAVE_DIR}/dlrm...")
        model.save(f"{self.SAVE_DIR}/dlrm")
        print(f"DLRM model saved successfully to {self.SAVE_DIR}/dlrm")

        # Proceed to the final step
        self.next(self.end)


    def load_schema(self, model_type, dataset):
        """Load and filter schema for Two-Tower model."""
        if model_type == 'retrieval':
            schema = dataset.schema.select_by_tag(["item_id", "user_id", "item", "user"]).without(['play_duration'])
        else:
            schema = dataset.schema
        return schema   


    @step
    def end(self):
        """
        End of the flow
        """
        print("Flow streaming. Happy for it.")

if __name__ == "__main__":
    TrainingFlow()    