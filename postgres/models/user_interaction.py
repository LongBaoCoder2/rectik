from .base import Base
from sqlalchemy import Column, Integer, ForeignKey, DateTime


class UserInteraction(Base):
    __tablename__ = 'user_interaction'
    
    user_id = Column(Integer, primary_key=True)
    video_id = Column(Integer, primary_key=True)
    play_duration = Column(Integer)  # milliseconds
    time = Column(DateTime)
