# sql_services/namespace_generator.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from project_config.postgres_config import DATABASE_URL
from project_models.namespace_models import Standard, Category, Subcategory

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def generate_namespace(category_name: str, subcategory_name: str, metric_short_key: str) -> str:
    session = Session()

    category = session.query(Category).filter_by(name=category_name).first()
    if not category:
        raise ValueError(f"Category '{category_name}' not found in database.")

    standard = session.query(Standard).filter_by(id=category.standard_id).first()
    if not standard:
        raise ValueError(f"No standard found for category '{category_name}'.")

    subcategory = session.query(Subcategory).filter_by(name=subcategory_name, category_id=category.id).first()
    if not subcategory:
        raise ValueError(f"Subcategory '{subcategory_name}' not found for category '{category_name}'.")

    namespace = f"{standard.name.lower()}.{category.name}.{subcategory.name}.{metric_short_key}"
    return namespace



