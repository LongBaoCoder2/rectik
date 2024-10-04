from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from .base import Base

class VideoInteraction(Base):
    __tablename__ = 'video_interaction'

    video_id = Column(Integer, primary_key=True)
    date = Column(Integer, primary_key=True)
    like_cnt = Column(Integer, default=0)
    like_user_num = Column(Integer, default=0)
    click_like_cnt = Column(Integer, default=0)
    double_click_cnt = Column(Integer, default=0)
    cancel_like_cnt = Column(Integer, default=0)
    cancel_like_user_num = Column(Integer, default=0)
    comment_cnt = Column(Integer, default=0)
    comment_user_num = Column(Integer, default=0)
    direct_comment_cnt = Column(Integer, default=0)
    reply_comment_cnt = Column(Integer, default=0)
    delete_comment_cnt = Column(Integer, default=0)
    delete_comment_user_num = Column(Integer, default=0)
    comment_like_cnt = Column(Integer, default=0)
    comment_like_user_num = Column(Integer, default=0)
    follow_cnt = Column(Integer, default=0)
    follow_user_num = Column(Integer, default=0)
    cancel_follow_cnt = Column(Integer, default=0)
    cancel_follow_user_num = Column(Integer, default=0)
    share_cnt = Column(Integer, default=0)
    share_user_num = Column(Integer, default=0)
    download_cnt = Column(Integer, default=0)
    download_user_num = Column(Integer, default=0)
    report_cnt = Column(Integer, default=0)
    report_user_num = Column(Integer, default=0)
    reduce_similar_cnt = Column(Integer, default=0)
    reduce_similar_user_num = Column(Integer, default=0)
    collect_cnt = Column(Integer, default=0)
    collect_user_num = Column(Integer, default=0)
    cancel_collect_cnt = Column(Integer, default=0)
    cancel_collect_user_num = Column(Integer, default=0)

    # Relationship to Video
    # video = relationship("Video", back_populates="interactions")