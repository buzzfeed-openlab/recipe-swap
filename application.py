from flask import redirect, request, render_template, Response, session, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import func
from functools import wraps
from jinja2 import evalcontextfilter, Markup, escape
import re

from app import create_app
from app.app_config import ADMIN_USER, ADMIN_PASS, SECRET_KEY
from app.models import Suggestion
from app.database import db



application = create_app()

@application.route("/")
def index():

    random_suggestion = Suggestion.query.filter_by(status_visible=True).order_by(func.rand()).first()

    # TODO: process urls so that they show up as working hyperlinks

    return render_template('index.html', random_suggestion=random_suggestion, is_permalink=False)


@application.route('/recipe/<suggestion_id>')
def recipe(suggestion_id):
    s = Suggestion.query.get(suggestion_id)

    # hide recipe if inappropriate
    if s and s.status_visible == False:
        s = None

    return render_template('index.html', random_suggestion=s, is_permalink=True)


@application.route("/contribute", methods=['GET', 'POST'])
def contribute():
    if request.method == 'POST':

        form_text = request.form['text']
        form_title = request.form['title']
        form_firstname = request.form['first_name']

        new = Suggestion(
            form_title,
            form_text,
            form_firstname
        )
        db.session.add(new)
        db.session.commit()

        return render_template('thanks.html')
    else:
        return render_template('contribute.html')


@application.route("/rollback", methods=['GET', 'POST'])
def rollback():
    # TODO: figure out what's going on???
    db.session.rollback()
    return redirect('/')


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
    review_queue = Suggestion.query\
                            .filter_by(status_flagged=True)\
                            .filter_by(status_reviewed=False)\
                            .all()
    visible = Suggestion.query\
                            .filter_by(status_visible=True)\
                            .all()
    return render_template('review.html', review_queue = review_queue, visible=visible)

@application.route('/reviewtrash')
@requires_auth
def reviewtrash():
    # TODO: suggestions that have been disapproved by moderator
    disapproved = Suggestion.query\
                            .filter_by(status_reviewed=True)\
                            .filter_by(status_visible=False)\
                            .all()
    return render_template('reviewtrash.html', disapproved=disapproved)


@application.route('/reviewrecipe/<suggestion_id>')
@requires_auth
def reviewrecipe(suggestion_id):
    s = Suggestion.query.get(suggestion_id)

    return render_template('reviewrecipe.html', suggestion=s)

@application.route('/flag/<suggestion_id>')
def flag(suggestion_id):
    s = Suggestion.query.get(suggestion_id)
    s.status_flagged = True

    # if this hasn't already been seen by moderator, hide from public
    if s.status_reviewed == False:
        s.status_visible = False

    db.session.commit()
    flash("ugh, sorry about that! thanks for reporting.")
    return redirect('/')


@application.route('/approve/<suggestion_id>')
@requires_auth
def approve(suggestion_id):
    s = Suggestion.query.get(suggestion_id)
    s.status_reviewed = True
    s.status_visible = True
    db.session.commit()
    return redirect('/review')

@application.route('/disapprove/<suggestion_id>')
@requires_auth
def disapprove(suggestion_id):
    s = Suggestion.query.get(suggestion_id)
    s.status_reviewed = True
    s.status_visible = False
    db.session.commit()
    return redirect('/review')


@application.route('/initialize')
@requires_auth
def initialize():
    db.create_all()
    return redirect('/')





@application.template_filter()
@evalcontextfilter
def nl2br(eval_ctx, value):
    _paragraph_re = re.compile(r'(?:\r\n|\r|\n){2,}')

    result = u'\n\n'.join(u'<p>%s</p>' % p.replace('\n', '<br>\n') \
        for p in _paragraph_re.split(escape(value)))
    if eval_ctx.autoescape:
        result = Markup(result)
    return result

@application.template_filter()
@evalcontextfilter
def url2link(eval_ctx, value):

    # DUCT TAPE: regex to turn urls into working links
    _url = re.compile(r'(?:(http://|https://)|(www\.))(\S+\b/?)([!"#$%&\'()*+,\-./:;<=>?@[\\\]^_`{|}~]*)(\s|$)', re.I)

    def replace(match):
        groups = match.groups()
        protocol = groups[0] or ''  # may be None
        www_lead = groups[1] or ''  # may be None
        return '<a href="{0}{1}{2}" target="_blank">{0}{1}{2}</a>{3}{4}'.format(
            protocol, www_lead, *groups[2:])

    result = _url.sub(replace, value)
    if eval_ctx.autoescape:
        result = Markup(result)

    return result





if __name__ == "__main__":

    application.run(host='0.0.0.0')
