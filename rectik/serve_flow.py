from metaflow import FlowSpec, step, batch, Parameter, current
import os


class ServingFlow(FlowSpec):
    BASE_DIR = Parameter(
        name='base_dir',
        default=os.environ.get("BASE_DIR", "/rectik/")
    )

    DATA_FOLDER = Parameter(
        name='data_folder',
        default=os.environ.get("DATA_FOLDER", "/rectik/data/")
    )

    TOPK_RETRIEVAL = Parameter(
        name='topk_retrieval',
        default=os.environ.get("TOPK_RETRIEVAL", "100")
    )

    TOPK_RERANK = Parameter(
        name='topk_rerank',
        default=os.environ.get("TOPK_RERANK", "10")
    )


    @step
    def start(self):
        """
        Start-up: check everything works or fail fast!
        """
        # Log start of the flow
        import os

        print(f"Starting the flow: {current.flow_name} | Run ID: {current.run_id} | User: {current.username}")
        
        # Check if Metaflow is using remote (S3) data store or local
        from metaflow.metaflow_config import DATASTORE_SYSROOT_S3 
        if DATASTORE_SYSROOT_S3:
            print("Using remote data store: S3")
        else:
            print("Local data store enabled")

        # define feature repo path
        self.feast_repo_path = os.path.join(self.BASE_DIR, "feast_repo/feature_repo/")
        print(f"Feast repository path set to: {self.feast_repo_path}")

        # Ensure directories exist
        if not os.path.isdir(os.path.join(self.BASE_DIR, 'faiss_index')):
            os.makedirs(os.path.join(self.BASE_DIR, 'faiss_index'))
        self.faiss_index_path = os.path.join(self.BASE_DIR, 'faiss_index', "index.faiss")
        print(f"Faiss index path set to: {self.faiss_index_path}")

        self.artifact_dir = os.path.join(self.BASE_DIR, "artifacts")
        self.retrieval_model_path = os.path.join(self.artifact_dir, "query_tower/")
        self.ranking_model_path = os.path.join(self.artifact_dir, "dlrm/")
        print(f"Artifact directory set to: {self.artifact_dir}")
        print(f"Retrieval model path: {self.retrieval_model_path}")
        print(f"Ranking model path: {self.ranking_model_path}")

        # Validate TOPK parameters
        assert int(self.TOPK_RERANK) and int(self.TOPK_RETRIEVAL)
        print(f"TOPK Retrieval: {self.TOPK_RETRIEVAL}, TOPK Rerank: {self.TOPK_RERANK}")

        # Validate date ranges
        self.next(self.setup_store)

    @step
    def setup_store(self):
        print("Starting setup for store and feature retrieval...")

        import os
        import numpy as np
        import pandas as pd
        import feast
        from nvtabular import ColumnSchema, Schema
        from nvtabular import Workflow
        from merlin.systems.dag.ensemble import Ensemble
        from merlin.systems.dag.ops.softmax_sampling import SoftmaxSampling
        from merlin.systems.dag.ops.tensorflow import PredictTensorflow
        from merlin.systems.dag.ops.unroll_features import UnrollFeatures
        from merlin.systems.dag.ops.workflow import TransformWorkflow
        from merlin.systems.dag.ops.faiss import QueryFaiss, setup_faiss
        from merlin.systems.dag.ops.feast import QueryFeast
        from merlin.dataloader.tf_utils import configure_tensorflow

        # Load item embeddings
        print("Loading item embeddings...")
        item_embeddings = pd.read_parquet(os.path.join(self.artifact_dir, "video_embeddings.parquet"))
        print(f"Item embeddings loaded with shape: {item_embeddings.shape}")

        # Setup FAISS
        print(f"Setting up FAISS with index path: {self.faiss_index_path}")
        setup_faiss(item_embeddings, 
                    self.faiss_index_path, 
                    embedding_column="output_1", item_id_column="video_id")

        # Set up Feast
        print("Setting up Feast feature store...")
        feature_store = feast.FeatureStore(self.feast_repo_path)

        # Set up user attributes
        print("Setting up user attributes...")
        user_attributes = ["user_id"] >> QueryFeast.from_feature_view(
            store=feature_store,
            view="user_features",
            column="user_id",
            include_id=True,
        )

        # Load and configure the NVT workflow for users
        print("Loading user subgraph from NVTabular workflow...")
        nvt_workflow = Workflow.load(os.path.join(self.DATA_FOLDER, 'processed/workflow'))
        user_subgraph = nvt_workflow.get_subworkflow("user")
        self.user_features = user_attributes >> TransformWorkflow(user_subgraph)

        # Configure TensorFlow
        print("Configuring TensorFlow for inference...")
        configure_tensorflow()

        # Set up the retrieval model and FAISS
        print("Setting up retrieval pipeline...")
        retrieval = (
            self.user_features
            >> PredictTensorflow(self.retrieval_model_path)
            >> QueryFaiss(self.faiss_index_path, topk=int(self.TOPK_RETRIEVAL))
        )

        # Retrieve video attributes
        print("Setting up video attributes...")
        video_attributes = retrieval["candidate_ids"] >> QueryFeast.from_feature_view(
            store=feature_store,
            view="video_features",
            column="candidate_ids",
            output_prefix="video",
            include_id=True,
        )

        # Load and configure the NVT workflow for videos
        print("Loading video subgraph from NVTabular workflow...")
        video_subgraph = nvt_workflow.get_subworkflow("video")
        video_features = video_attributes >> TransformWorkflow(video_subgraph)

        # Unroll user features and video features
        print("Unrolling features for ranking model...")
        user_features_to_unroll = [
            "user_id",
            "onehot_feat0", "onehot_feat1", "onehot_feat2", "onehot_feat3", 
            "onehot_feat5", "onehot_feat6", "onehot_feat7", "onehot_feat8", 
            "onehot_feat9", "onehot_feat10", "onehot_feat11", "onehot_feat4",
            "onehot_feat12", "onehot_feat13", "onehot_feat14", "onehot_feat15", 
            "onehot_feat16", "onehot_feat17",
            "is_lowactive_period", "is_live_streamer", "is_video_author",
            "follow_user_num_range", "fans_user_num_range", "friend_user_num_range", 
            "register_days_range"
        ]

        combined_features = video_features >> UnrollFeatures(
            "video_id", self.user_features[user_features_to_unroll]
        )

        # Predict rankings
        print("Running ranking model...")
        ranking = combined_features >> PredictTensorflow(self.ranking_model_path)

        # Apply softmax sampling for final ranking
        print("Applying softmax sampling for top-k reranking...")
        ordering = combined_features["video_id"] >> SoftmaxSampling(
            relevance_col=ranking["play_duration/regression_task"], topk=int(self.TOPK_RERANK), temperature=0.00000001
        )

        # Create ensemble directory if it doesn't exist
        if not os.path.isdir(os.path.join(self.artifact_dir, 'poc_ensemble')):
            os.makedirs(os.path.join(self.artifact_dir, 'poc_ensemble'))

        print(f"Ensemble directory created at: {os.path.join(self.artifact_dir, 'poc_ensemble')}")

        # Define request schema and export the ensemble
        print("Defining request schema and exporting ensemble...")
        request_schema = Schema(
            [
                ColumnSchema("user_id", dtype=np.int32),
            ]
        )

        export_path = os.path.join(self.artifact_dir, 'poc_ensemble')
        ensemble = Ensemble(ordering, request_schema)
        ens_config, node_configs = ensemble.export(export_path)

        print(f"Setup Successfully. Models and config exported to: {export_path}")

        self.next(self.end)


    @step
    def end(self):
        """
        End of the flow
        """
        print("Flow completed successfully.")


if __name__ == "__main__":
    ServingFlow()
