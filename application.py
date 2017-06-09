from flask import redirect, request, render_template, Response, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import func
from functools import wraps

from app import create_app
from app.app_config import ADMIN_USER, ADMIN_PASS, SECRET_KEY
from app.models import Suggestion
from app.database import db



application = create_app()

@application.route("/")
def index():
    # TODO: grab some recordings to show
    return render_template('index.html')



@application.route("/rollback", methods=['GET', 'POST'])
def rollback():
    # TODO: figure out what's going on???
    db.session.rollback()
    return redirect('/respond')


def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    return username == ADMIN_USER and password == ADMIN_PASS

def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Could not verify your credentials for that url', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated


@application.route('/review')
@requires_auth
def review():
    # TODO: suggestions that are flagged and haven't been moderated
    review_queue = Suggestion.query.filter_by(public_flagged=True).all()
    return render_template('review.html', review_queue = review_queue)

@application.route('/reviewtrash')
@requires_auth
def reviewtrash():
    # TODO: suggestions that have been disapproved by moderator
    disapproved = Suggestion.query.filter_by(moderator_flagged=True).all()
    return render_template('reviewtrash.html', disapproved=disapproved)


@application.route('/approve/<suggestion_id>')
@requires_auth
def approve(suggestion_id):
    s = Suggestion.query.get(suggestion_id)
    s.is_approved = True
    db.session.commit()
    return redirect('/review')

@application.route('/disapprove/<suggestion_id>')
@requires_auth
def disapprove(suggestion_id):
    s = Suggestion.query.get(suggestion_id)
    s.is_approved = False
    db.session.commit()
    return redirect('/review')


@application.route('/initialize')
@requires_auth
def initialize():
    # TODO: only do this if tables don't exist?
    db.create_all()
    return redirect('/')



if __name__ == "__main__":

    application.secret_key = SECRET_KEY
    application.run(debug=True, host='0.0.0.0')
