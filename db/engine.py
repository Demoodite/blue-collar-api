from sqlmodel import create_engine

from .models import *

engine = create_engine("sqlite:///bcollar.db", echo=True)
