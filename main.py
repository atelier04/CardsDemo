import base64
from datetime import datetime
from io import BytesIO

from flask import Flask, render_template, request, redirect, url_for, send_file
from flask_sqlalchemy import SQLAlchemy
from dbconfig import DB_URI
from sqlalchemy import Column, Integer, DATETIME, BINARY, String, UnicodeText, create_engine, or_
from sqlalchemy.orm import relationship, session, sessionmaker
import json
from PIL import Image

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
    image_file = Column(db.LargeBinary, nullable=True, name="image_file")
    category_id = Column(db.Integer, db.ForeignKey("category.category_id"), name="category_id")

    def __repr__(self):
        return f"{self.title} {self.description} {self.created_at}"

    def to_dict(self):
        return {'title': self.title, 'description': self.description,
                'created_at': str(self.created_at),
                'category_id': self.category_id
                }


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
    pass
    # session1.commit()
from models import count

with app.app_context():
    db.create_all()
    # category1: Category = Category(title="title1", description="desc1", created_at=datetime.now())
    # db.session.add(category1)
    """
    category = Category.query.filter(Category.category_id == 1).first()
    card1 = Card(title="title1", description="desc1", created_at=datetime.now())
    card2 = Card(title="title2", description="desc2", created_at=datetime.now())
    card3 = Card(title="title3", description="desc3", created_at=datetime.now())

    category.cards.append(card1)
    category.cards.append(card2)
    category.cards.append(card3)
    db.session.add(card1)
    db.session.add(card2)
    db.session.add(card3)
    """
    db.session.commit()
    count += 1
    print(f"Database created {count}")


@app.get("/cards")
def get_cards():
    cards: list = []
    if "search_result" in request.args:
        print(f"{request.args.get('search_result')}")
        # cards = request.args.get('search_result',type=list)
        cards = json.loads(request.args.get('search_result'))
        print(f"in get_cards {type(cards)=}")
        print(f"in get_cards {cards=}")
    else:
        cards: list[Card] = Card.query.all()
        for index, card in enumerate(cards):
            if card.image_file is not None:
                file_img = cards[index].image_file

                img: Image = Image.open(BytesIO(file_img))
                card_image_id = str(cards[index].card_id)
                img.save(f"static/img/{cards[index].card_id}.png")
    # return send_file(BytesIO(file_img),as_attachment=True,download_name="test.png")

    return render_template("cards.html", cards=cards)


@app.post("/cards_search")
def cards_search():
    search = request.form.get("search")
    cards = Card.query.filter(or_(Card.title == search, Card.description == search)).all()
    print(f"In card search {cards=}")
    print(f"{type(cards)=}")
    cards = json.dumps([card.to_dict() for card in cards])

    # cards=json.dumps(cards)
    # , search_result=cards
    return redirect(url_for("get_cards", search_result=cards))


@app.route("/cards/card_add_form", methods=['GET', 'POST'])
def card_add_form():
    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description")
        card: Card = Card(title=title, description=description, created_at=datetime.now())
        category_id = request.form.get("category")

        print(f"{category_id=}")
        image_file = request.files.get("file")
        print(image_file.name, image_file.filename)
        card.image_file = image_file.read()
        print(f"{image_file=}")
        category: Category = Category.query.filter(Category.category_id == category_id).first()
        category.cards.append(card)
        db.session.add(card)
        db.session.commit()
        return redirect("/cards")
    else:
        print(f"{request.method=}")
        categories = Category.query.all()
        return render_template("card_add_form.html", categories=categories)


@app.get("/cards/<int:card_id>")
def get_card(card_id):
    card_return = Card.query.filter(Card.card_id == card_id).first()
    return render_template("card.html", card=card_return)


@app.get("/cards/delete/<int:card_id>")
def delete_card(card_id):
    card_return = Card.query.filter(Card.card_id == card_id).first()
    db.session.delete(card_return)
    db.session.commit()
    return redirect(url_for('get_cards'))


@app.route("/cards/update/<int:card_id>", methods=['GET', 'POST'])
def card_update_form(card_id):
    if request.method == "GET":
        card_return = Card.query.filter(Card.card_id == card_id).first()
        categories = Category.query.all()
        return render_template("card_update_form.html", card=card_return, categories=categories)
    else:
        title = request.form.get("title")
        description = request.form.get("description")
        category_id = request.form.get("category")
        card_return = Card.query.filter(Card.card_id == card_id).first()
        card_return.title = title
        card_return.description = description
        card_return.category_id = category_id
        if request.files.get("file") is not None:
            card_return.image_file = request.files.get("file").read()
        db.session.commit()
        return redirect(url_for('get_cards'))


@app.route("/cards/add_category", methods=['GET', 'POST'])
def add_category():
    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description")
        category: Category = Category(title=title, description=description, created_at=datetime.now())
        db.session.add(category)
        db.session.commit()
        return redirect("/cards")
    else:
        print(f"{request.method=}")
        return render_template("category_form.html")


if __name__ == '__main__':
    app.run(debug=True, host="localhost")
