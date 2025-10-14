from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    hashed_password = db.Column(db.String(255), nullable=False)
    created_date = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # связь "один ко многим" (автор → статьи)
    articles = db.relationship('Article', backref='author', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<User {self.name}>'


class Article(db.Model):
    __tablename__ = 'article'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    text = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), default="general") 
    created_date = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Связь одна статья — много комментариев
    comments = db.relationship('Comment', backref='article', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Article {self.title}>'


class Comment(db.Model):
    __tablename__ = 'comment'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    created_date = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    article_id = db.Column(db.Integer, db.ForeignKey('article.id'), nullable=False)
    author_name = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'<Comment {self.id}>'