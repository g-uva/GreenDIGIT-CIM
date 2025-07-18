# project_models/namespace_models.py

from sqlalchemy import Column, Integer, String, Text, ForeignKey, ARRAY
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Standard(Base):
    __tablename__ = "standards"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text)

    categories = relationship("Category", back_populates="standard")

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    standard_id = Column(Integer, ForeignKey("standards.id"))
    description = Column(Text)

    standard = relationship("Standard", back_populates="categories")
    subcategories = relationship("Subcategory", back_populates="category")

class Subcategory(Base):
    __tablename__ = "subcategories"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"))
    description = Column(Text)

    category = relationship("Category", back_populates="subcategories")

class MetricDefinition(Base):
    __tablename__ = "metric_definitions"
    id = Column(Integer, primary_key=True)
    unified_key = Column(String, unique=True, nullable=False)
    subcategory_id = Column(Integer, ForeignKey("subcategories.id"))
    source_keys = Column(ARRAY(Text))
    tags = Column(ARRAY(Text))
