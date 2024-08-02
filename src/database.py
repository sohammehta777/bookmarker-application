from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy.sql import func
import string
import random
from typing import List, Optional
from sqlalchemy.orm import Mapped, mapped_column, relationship

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(db.String(80), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(db.String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(db.Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=func.now())
    bookmarks: Mapped[List["Bookmark"]] = relationship("Bookmark", back_populates="user")

    def __repr__(self) -> str:
        return f'User>>> {self.username}'


class Bookmark(db.Model):
    __tablename__ = 'bookmark'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    body: Mapped[Optional[str]] = mapped_column(db.Text, nullable=True)
    url: Mapped[str] = mapped_column(db.Text, nullable=False)
    short_url: Mapped[str] = mapped_column(db.String(3), nullable=False)
    visits: Mapped[int] = mapped_column(db.Integer, default=0)
    user_id: Mapped[int] = mapped_column(db.ForeignKey('user.id'))
    created_at: Mapped[datetime] = mapped_column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=func.now())
    user: Mapped["User"] = relationship("User", back_populates="bookmarks")

    def generate_short_characters(self) -> str:
        characters = string.digits + string.ascii_letters
        picked_chars = ''.join(random.choices(characters, k=3))
        
        link = self.query.filter_by(short_url=picked_chars).first()
        
        if link:
            return self.generate_short_characters()
        else:
            return picked_chars

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.short_url = self.generate_short_characters()

    def __repr__(self) -> str:
        return f'Bookmark>>> {self.url}'