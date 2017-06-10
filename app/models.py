import datetime

from app.database import db


class Suggestion(db.Model):
    title = db.Column(db.Text)
    text = db.Column(db.Text)
    first_name = db.Column(db.Text)

    id = db.Column(db.Integer, primary_key=True)
    status_flagged = db.Column(db.Boolean, default=False)
    status_reviewed = db.Column(db.Boolean, default=False)
    status_visible = db.Column(db.Boolean)
    view_count = db.Column(db.Integer)
    dt = db.Column(db.DateTime, default=datetime.datetime.now)

    def __init__(self, title, text, first_name):
        self.title = title
        self.text = text
        self.first_name = first_name
        self.view_count = 0

        # TODO: set this as a config variable?
        self.status_visible = True


    def __repr__(self):
        return '<Suggestion %r %r>' % (self.first_name, self.title[:10])
