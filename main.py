from datetime import datetime

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dbconfig import DB_URI
from sqlalchemy import Column, Integer, DATETIME, String, UnicodeText, create_engine
from sqlalchemy.orm import relationship, session, sessionmaker

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
db: SQLAlchemy = SQLAlchemy()
db.init_app(app)
engine = create_engine(DB_URI)
Session = sessionmaker(bind=engine)


class Card(db.Model):
    card_id = Column(Integer, name="card_id", primary_key=True, autoincrement=True)
    title = Column(db.String, name="title", nullable=False)
    description = Column(db.String, name="description", nullable=False)
    created_at = Column(db.DateTime, default=datetime.now())
    category_id = Column(db.Integer, db.ForeignKey("category.category_id"), name="category_id", )

    def __repr__(self):
        return f"{self.title} {self.description} {self.created_at}"


class Category(db.Model):
    __tablename__ = "category"
    category_id = Column(Integer, name="category_id", primary_key=True, autoincrement=True)
    title = Column(db.String, name="title", nullable=False)
    description = Column(db.String, name="description", nullable=False)
    created_at = Column(db.DateTime, name="created_at", nullable=False)
    cards = relationship("Card")

    def __repr__(self):
        return f"{self.title} {self.description} {self.created_at}"


with Session() as session1:
    #category1: Category = Category(title="title1", description="desc1", created_at=datetime.now())
    #session1.add(category1)

    session1.commit()

with app.app_context():
    db.create_all()
    category = Category.query.filter(Category.category_id == 1).first()
    card1 = Card(title="title1", description="desc1",created_at=datetime.now())
    print(f"{type(category)}")
    print(f"{category}")
    category.cards.append(card1)
    db.session.add(card1)
    db.session.commit()

    print(f"Database created")

if __name__ == '__main__':

    app.run(debug=True, host="localhost")
