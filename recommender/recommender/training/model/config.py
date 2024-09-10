class MultiModalSSLConfig:
    """
    A configuration class to hold and manage hyperparameters for the MMSSL model.

    Attributes:
    ----------
    device: str | torch.device
        Device to use for training (default='cuda').
    embedding_dim : int
        Embedding size for users, items, and multimodal features (default=128).
    drop_rate : float
        Dropout rate for regularization (default=0.3).
    head_num : int
        Number of attention heads (default=8).
    weight_size : list
        Hidden layer sizes for the model (default=[64, 32]).
    learning_rate : float
        Learning rate for optimization (default=0.001).
    batch_size : int
        Batch size for training (default=128).
    num_epochs : int
        Number of epochs for training (default=50).
    tau : float
        Temperature for self-supervised loss (default=0.5).
    n_users : int
        Number of users in the dataset (default=1000).
    n_items : int
        Number of items in the dataset (default=1000).
    image_feat_dim : int
        Dimension of image features (default=2048).
    text_feat_dim : int
        Dimension of text features (default=768).
    use_pretrained_embeddings : bool
        Whether to use pre-trained embeddings (default=True).
    is_freeze_embeddings : bool
        Whether to freeze the embeddings (default=True).
    layers : int
        Number of layers for the model (default=2).
    id_cat_rate : float
        Rate for categorical embeddings (default=0.5).
    model_cat_rate : float
        Rate for model embeddings (default=0.5).
    """ 
    
    def __init__(self,
                 device='cuda',
                 embedding_dim=128,
                 drop_rate=0.3,
                 head_num=8,
                 weight_size=[64, 32],
                 learning_rate=0.001,
                 batch_size=128,
                 num_epochs=50,
                 tau=0.5,
                 n_users=1000,
                 n_items=1000,
                 image_feat_dim=2048,
                 text_feat_dim=768,
                 use_pretrained_embeddings=True,
                 is_freeze_embeddings=True,
                 layers=2,
                 id_cat_rate=0.5,
                 model_cat_rate=0.5):
        self.device = device
        self.embedding_dim = embedding_dim
        self.drop_rate = drop_rate
        self.head_num = head_num
        self.weight_size = weight_size
        self.learning_rate = learning_rate
        self.batch_size = batch_size
        self.num_epochs = num_epochs
        self.tau = tau
        self.n_users = n_users
        self.n_items = n_items
        self.image_feat_dim = image_feat_dim
        self.text_feat_dim = text_feat_dim
        self.use_pretrained_embeddings = use_pretrained_embeddings
        self.is_freeze_embeddings = is_freeze_embeddings
        self.layers = layers
        self.id_cat_rate = id_cat_rate
        self.model_cat_rate = model_cat_rate