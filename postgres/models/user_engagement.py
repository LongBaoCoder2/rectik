from sqlalchemy import Column, Integer, ForeignKey
from .base import Base

class UserEngagement(Base):
    __tablename__ = 'user_engagement'

    video_id = Column(Integer, primary_key=True)
    date = Column(Integer, primary_key=True)
    report_cnt = Column(Integer, default=0)
    report_user_num = Column(Integer, default=0)
    reduce_similar_cnt = Column(Integer, default=0)
    reduce_similar_user_num = Column(Integer, default=0)
    collect_cnt = Column(Integer, default=0)
    collect_user_num = Column(Integer, default=0)
    cancel_collect_cnt = Column(Integer, default=0)
    cancel_collect_user_num = Column(Integer, default=0)
