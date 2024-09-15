import torch
import torch.nn as nn
import torch.nn.functional as F
from .config import MultiModalSSLConfig
from .model import BaseTrainingModel

class MultiModalSSL(BaseTrainingModel):
    def __init__(self, config: MultiModalSSLConfig):
        super().__init__()
        
        # User and item embedding parameters
        self.n_users = config.n_users
        self.n_items = config.n_items
        self.embedding_dim = config.embedding_dim
        self.weight_size = [self.embedding_dim] + config.weight_size
        self.layers = config.layers
        self.id_cat_rate = config.id_cat_rate
        self.model_cat_rate = config.model_cat_rate
        self.drop_rate = config.drop_rate
        self.head_num = config.head_num
        self.tau = config.tau
        
        # Initializing image and text transformations
        self.image_trans, self.text_trans = self.init_modal_encoders()
        self.encoder = nn.ModuleDict({
            'image_encoder': self.image_trans,
            'text_encoder': self.text_trans,
        })
        
        # Common transformation layers
        self.common_trans = self.init_common_transform()
        self.align = nn.ModuleDict({'common_trans': self.common_trans})

        # User and Item ID embeddings
        self.user_id_embedding, self.item_id_embedding = self.init_embeddings()
        
        # Pre-trained or standard embeddings
        self.image_embedding, self.text_embedding = self.init_modal_embeddings(config)
        
        # Additional components
        self.softmax = nn.Softmax(dim=-1)
        self.act = nn.Sigmoid()  
        self.sigmoid = nn.Sigmoid()
        self.dropout = nn.Dropout(p=config.drop_rate)
        self.batch_norm = nn.BatchNorm1d(self.embedding_dim)
        self.tau = config.tau
        
        # Attention weight initialization
        self.weight_dict = self.init_attention_weights(config)
        
        # Placeholder dictionaries
        self.embedding_dict = {'user': {}, 'item': {}}

    def init_modal_encoders(self, config):
        """Initialize image and text transformation layers."""
        image_trans = nn.Linear(config.image_feat_dim, self.embedding_dim)
        text_trans = nn.Linear(config.text_feat_dim, self.embedding_dim)
        nn.init.xavier_uniform_(image_trans.weight)
        nn.init.xavier_uniform_(text_trans.weight)
        return image_trans, text_trans

    def init_common_transform(self):
        """Initialize common transformation layer."""
        common_trans = nn.Linear(self.embedding_dim, self.embedding_dim)
        nn.init.xavier_uniform_(common_trans.weight)
        return common_trans
    
    def init_embeddings(self):
        """Initialize user and item embeddings."""
        user_id_embedding = nn.Embedding(self.n_users, self.embedding_dim)
        item_id_embedding = nn.Embedding(self.n_items, self.embedding_dim)
        nn.init.xavier_uniform_(user_id_embedding.weight)
        nn.init.xavier_uniform_(item_id_embedding.weight)
        return user_id_embedding, item_id_embedding
    
    def init_modal_embeddings(self, config):
        """Initialize image and text embeddings (either pretrained or standard)."""
        if config.use_pretrained_embeddings:
            image_embedding = nn.Embedding.from_pretrained(config.image_feats, freeze=config.is_freeze_embeddings)
            text_embedding = nn.Embedding.from_pretrained(config.text_feats, freeze=config.is_freeze_embeddings)
        else:
            image_embedding = nn.Embedding(self.n_items, config.image_feat_dim)
            text_embedding = nn.Embedding(self.n_items, config.text_feat_dim)
            nn.init.xavier_uniform_(image_embedding.weight)
            nn.init.xavier_uniform_(text_embedding.weight)
        return image_embedding, text_embedding
    
    def init_attention_weights(self, config):
        """Initialize weights for attention mechanisms."""
        initializer = nn.init.xavier_uniform_
        return nn.ParameterDict({
            'w_q': nn.Parameter(initializer(torch.empty([self.embedding_dim, self.embedding_dim]))),
            'w_k': nn.Parameter(initializer(torch.empty([self.embedding_dim, self.embedding_dim]))),
            'w_v': nn.Parameter(initializer(torch.empty([self.embedding_dim, self.embedding_dim]))),
            'w_self_attention_item': nn.Parameter(initializer(torch.empty([self.embedding_dim, self.embedding_dim]))),
            'w_self_attention_user': nn.Parameter(initializer(torch.empty([self.embedding_dim, self.embedding_dim]))),
            'w_self_attention_cat': nn.Parameter(initializer(torch.empty([config.head_num * self.embedding_dim, self.embedding_dim]))),
        })

    def forward(self, ui_graph, iu_graph, image_ui_graph, image_iu_graph, text_ui_graph, text_iu_graph):

        image_feats = image_item_feats = self.dropout(self.image_trans(self.image_feats))
        text_feats = text_item_feats = self.dropout(self.text_trans(self.text_feats))

        for i in range(self.layers):
            image_user_feats = self.mm(ui_graph, image_feats)
            image_item_feats = self.mm(iu_graph, image_user_feats)
            image_user_id = self.mm(image_ui_graph, self.item_id_embedding.weight)
            image_item_id = self.mm(image_iu_graph, self.user_id_embedding.weight)

            text_user_feats = self.mm(ui_graph, text_feats)
            text_item_feats = self.mm(iu_graph, text_user_feats)

            text_user_id = self.mm(text_ui_graph, self.item_id_embedding.weight)
            text_item_id = self.mm(text_iu_graph, self.user_id_embedding.weight)

        self.embedding_dict['user']['image'] = image_user_id
        self.embedding_dict['user']['text'] = text_user_id
        self.embedding_dict['item']['image'] = image_item_id
        self.embedding_dict['item']['text'] = text_item_id
        user_z, _ = self.multi_head_self_attention(self.weight_dict, self.embedding_dict['user'], self.embedding_dict['user'])
        item_z, _ = self.multi_head_self_attention(self.weight_dict, self.embedding_dict['item'], self.embedding_dict['item'])
        user_emb = user_z.mean(0)
        item_emb = item_z.mean(0)
        u_g_embeddings = self.user_id_embedding.weight + self.id_cat_rate*F.normalize(user_emb, p=2, dim=1)
        i_g_embeddings = self.item_id_embedding.weight + self.id_cat_rate*F.normalize(item_emb, p=2, dim=1)

        user_emb_list = [u_g_embeddings]
        item_emb_list = [i_g_embeddings]
        for i in range(self.n_ui_layers):    
            if i == (self.n_ui_layers-1):
                u_g_embeddings = self.softmax( torch.mm(ui_graph, i_g_embeddings) ) 
                i_g_embeddings = self.softmax( torch.mm(iu_graph, u_g_embeddings) )

            else:
                u_g_embeddings = torch.mm(ui_graph, i_g_embeddings) 
                i_g_embeddings = torch.mm(iu_graph, u_g_embeddings) 

            user_emb_list.append(u_g_embeddings)
            item_emb_list.append(i_g_embeddings)

        u_g_embeddings = torch.mean(torch.stack(user_emb_list), dim=0)
        i_g_embeddings = torch.mean(torch.stack(item_emb_list), dim=0)


        u_g_embeddings = u_g_embeddings + self.model_cat_rate*F.normalize(image_user_feats, p=2, dim=1) + self.model_cat_rate*F.normalize(text_user_feats, p=2, dim=1)
        i_g_embeddings = i_g_embeddings + self.model_cat_rate*F.normalize(image_item_feats, p=2, dim=1) + self.model_cat_rate*F.normalize(text_item_feats, p=2, dim=1)

        return u_g_embeddings, i_g_embeddings, image_item_feats, text_item_feats, image_user_feats, text_user_feats, u_g_embeddings, i_g_embeddings, image_user_id, text_user_id, image_item_id, text_item_id
