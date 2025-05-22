from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import scoped_session, sessionmaker

db = SQLAlchemy()

class Database:
    def __init__(self):
        self._db = db
        self._session_factory = None
        self._scoped_session = None

    @property
    def db(self):
        return self._db

    # def init_db(self, app: Flask):
    #     """Initialize the database with Flask app"""
    #     self._db.init_app(app)

    def get_session(self):
        """Get or create scoped session"""
        # if not self._scoped_session:
        #     if not self._db.engine:
        #         raise RuntimeError("Database not initialized. Call init_db first.")
        #     self._session_factory = sessionmaker(bind=self._db.engine)
        #     self._scoped_session = scoped_session(self._session_factory)
        return self._db.session