from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Article(Base):
    __tablename__ = 'articles'
    article_id = Column(Integer, autoincrement=True, primary_key=True)
    article_author = Column(String, nullable=False)
    article_title = Column(String, nullable=False)
    article_snippet = Column(String, nullable=False)
    article_content = Column(String, nullable=False)