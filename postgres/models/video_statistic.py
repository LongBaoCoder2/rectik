from sqlalchemy import Column, Integer, Float, ForeignKey
from .base import Base
from sqlalchemy.orm import relationship

class VideoStatistic(Base):
    __tablename__ = 'video_statistic'

    video_id = Column(Integer, primary_key=True)
    date = Column(Integer, primary_key=True)
    show_cnt = Column(Integer, default=0)
    show_user_num = Column(Integer, default=0)
    play_cnt = Column(Integer, default=0)
    play_user_num = Column(Integer, default=0)
    play_duration = Column(Integer, default=0)
    complete_play_cnt = Column(Integer, default=0)
    complete_play_user_num = Column(Integer, default=0)
    valid_play_cnt = Column(Integer, default=0)
    valid_play_user_num = Column(Integer, default=0)
    long_time_play_cnt = Column(Integer, default=0)
    long_time_play_user_num = Column(Integer, default=0)
    short_time_play_cnt = Column(Integer, default=0)
    short_time_play_user_num = Column(Integer, default=0)
    play_progress = Column(Float, default=0.0)
    comment_stay_duration = Column(Integer, default=0)

    # Relationship to Video
    # video = relationship("Video", back_populates="statistics")