from flask_wtf import FlaskForm
from wtforms import StringField
from flask_pagedown.fields import PageDownField
from wtforms.fields import SubmitField

class PostForm(FlaskForm):
    title = StringField('Title')
    author = StringField('Author')
    snippet = StringField('Brief summary')
    pagedown = PageDownField('Content')
    submit = SubmitField('Submit')
