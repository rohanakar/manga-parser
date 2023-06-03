from sqlalchemy import Boolean, CheckConstraint, Column, Integer, String
from domain.base import Base

class Manga(Base):
    __tablename__ = 'Manga'

    id = Column(Integer, primary_key=True, autoincrement=True)
    folder = Column(String(255), nullable=False)
    status = Column(Integer, default=False)
    __table_args__ = (
        CheckConstraint(status.between(0, 3), name='check_status_range'),
    )

    def __repr__(self):
        return f"Manga(id={self.id}, folder={self.folder}, status={self.status})"
        