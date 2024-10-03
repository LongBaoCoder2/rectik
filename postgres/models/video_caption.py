from sqlalchemy import Column, Integer, String, ForeignKey
from .base import Base

class VideoCaption(Base):
    __tablename__ = 'video_caption'

    video_id = Column(Integer, primary_key=True)
    manual_cover_text = Column(String, nullable=True)
    caption = Column(String, nullable=True)
    topic_tag = Column(String, nullable=True)
    first_level_category_name = Column(String, nullable=True)
    second_level_category_name = Column(String, nullable=True)
    third_level_category_name = Column(String, nullable=True)
