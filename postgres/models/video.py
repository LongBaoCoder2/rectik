from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Float
from .base import Base
from sqlalchemy.orm import relationship

class Video(Base):
    __tablename__ = 'video'
    
    video_id = Column(Integer, primary_key=True, autoincrement=True)
    author_id = Column(Integer,nullable=False)
    # video_type = Column(String, nullable=False)
    upload_dt = Column(DateTime, nullable=False)
    upload_type = Column(String, nullable=False) 
    visible_status = Column(String, nullable=False)    # Constraint: ['public', 'private', 'only friends']
    video_duration = Column(Float, nullable=False)
    video_width = Column(Integer, nullable=False)
    video_height = Column(Integer, nullable=False)
    music_id = Column(Integer, nullable=True)

    # Relationships to other models
    # interactions = relationship("VideoInteraction", back_populates="video")
    # statistics = relationship("VideoStatistic", back_populates="video")