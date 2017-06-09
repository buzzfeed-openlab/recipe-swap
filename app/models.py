import datetime

from app.database import db


class Suggestion(db.Model):
    title = db.Column(db.Text)
    text = db.Column(db.Text)
    first_name = db.Column(db.Text)

    id = db.Column(db.Integer, primary_key=True)
    public_flagged = db.Column(db.Boolean)
    moderator_flagged = db.Column(db.Boolean)
    view_count = db.Column(db.Integer)
    dt = db.Column(db.DateTime, default=datetime.datetime.now)

    def __init__(self, first_name, title, text):
        self.first_name = first_name
        self.title = title
        self.text = text
        self.view_count = 0


    def __repr__(self):
        return '<Suggestion %r %r>' % (self.first_name, self.title[:10])
