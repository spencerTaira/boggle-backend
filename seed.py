from app import app
from database import db


# import all models - necessary for create_all()

db.drop_all()
db.create_all()
