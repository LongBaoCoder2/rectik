from sqlalchemy import Column, Integer, String, CheckConstraint
from sqlalchemy.orm import relationship
from .base import Base

class User(Base):
    __tablename__ = 'user'
    __table_args__ = (
        CheckConstraint(("user_active_degree in ('full_active',  \
                         'high_active', 'middle_active', 'UNKNOWN')")),
    )

    user_id = Column(Integer, primary_key=True)
    user_active_degree = Column(String)
    is_lowactive_period = Column(Integer)
    is_live_streamer = Column(Integer)
    is_video_author = Column(Integer)
    follow_user_num = Column(Integer)
    follow_user_num_range = Column(String) # 
    fans_user_num = Column(Integer)
    fans_user_num_range = Column(String) #
    friend_user_num = Column(Integer)
    friend_user_num_range = Column(String) #
    register_days = Column(Integer)
    register_days_range = Column(String) #

    # Back-populate relationship with Friend
    # interactions = relationship("Friend", back_populates="user")
