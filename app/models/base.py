# Author: SANJAY KR
from .. import db

def init_db():
    db.create_all()

def get_db():
    return db.session
