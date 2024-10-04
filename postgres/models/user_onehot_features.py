from sqlalchemy import Column, Integer, ForeignKey
from .base import Base

class UserOnehotFeatures(Base):
    __tablename__ = 'user_onehot_features'

    user_id = Column(Integer ,primary_key=True)
    onehot_feat0 = Column(Integer)
    onehot_feat1 = Column(Integer)
    onehot_feat2 = Column(Integer)
    onehot_feat3 = Column(Integer)
    onehot_feat4 = Column(Integer)
    onehot_feat5 = Column(Integer)
    onehot_feat6 = Column(Integer)
    onehot_feat7 = Column(Integer)
    onehot_feat8 = Column(Integer)
    onehot_feat9 = Column(Integer)
    onehot_feat10 = Column(Integer)
    onehot_feat11 = Column(Integer)
    onehot_feat12 = Column(Integer)
    onehot_feat13 = Column(Integer)
    onehot_feat14 = Column(Integer)
    onehot_feat15 = Column(Integer)
    onehot_feat16 = Column(Integer)
    onehot_feat17 = Column(Integer)
