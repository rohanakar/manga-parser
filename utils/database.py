import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from domain.base import Base
from domain.manga import Manga

logger = logging.getLogger(__name__)

engine = create_engine('sqlite:///sample.db', echo=False)
Session = sessionmaker(bind=engine)
Base.metadata.create_all(engine)

def save(obj):
    session = Session()
    session.add(obj)
    session.commit()
    session.close()

def getAll(obj):
    session = Session()
    response = session.query(obj).all()
    session.close()
    return response

def get(obj,filter_query):
    session = Session()
    response = session.query(obj).filter(filter_query).all()
    session.close()
    return response

def remove(obj,filter_query):
    session = Session()
    response = session.query(obj).filter(filter_query).first()
    session.delete(response)
    session.commit()
    session.close()
