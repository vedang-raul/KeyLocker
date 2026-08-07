from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from db.db import Base


class MonitoredAPI(Base):
    __tablename__ = "monitored_apis"

    monitor_id = Column(Integer, primary_key=True, index=True)

    provider = Column(String, nullable=False)  # e.g. "openai", "anthropic"
    label = Column(String, nullable=False)  # admin-facing nickname
    api_key = Column(String, nullable=False)

    added_by = Column(Integer, ForeignKey("users.emp_id", ondelete="CASCADE"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    added_by_user = relationship("Users", lazy="selectin")
