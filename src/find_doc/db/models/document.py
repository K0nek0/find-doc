from sqlalchemy import JSON, Column, DateTime, Integer, String, func

from find_doc.db.base import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    rubrics = Column(JSON, nullable=True)
    text = Column(String, nullable=False)
    created_date = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<Document id={self.id}>"
