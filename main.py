from datetime import datetime

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dbconfig import DB_URI
from sqlalchemy import Column, Integer, DATETIME, String, UnicodeText

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
db: SQLAlchemy = SQLAlchemy(app)

class Card(db.Model):
    card_id = Column(Integer, name="card_id", primary_key=True, autoincrement=True)
    title = Column(db.String, name="title")
    description = Column(db.String, name="description", nullable=False)
    created_at = Column(db.DateTime, default=datetime.now())

    def __repr__(self):
        return f"{self.name}"


with app.app_context():
    db.create_all()
    db.session.commit()
    print(f"Database created")

if __name__ == '__main__':
    app.run(debug=True, host="localhost")
