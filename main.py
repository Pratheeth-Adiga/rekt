import os

from flask import Flask, request, render_template, redirect
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_cockroachdb import run_transaction
from sqlalchemy.orm.exc import NoResultFound
from markupsafe import Markup

from flask_pagedown import PageDown
import markdown
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from models import Article
from form import PostForm

app = Flask(__name__)
pagedown = PageDown(app)
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "80 per hour"]
)

SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY

db_uri = os.environ['DATABASE_URL'].replace("postgresql://", "cockroachdb://")


try:
    engine = create_engine(db_uri)
except Exception as e:
    print("Failed to connect to database.")
    print(f"{e}")

def fetch_articles(session):
    try:
        articles = session.query(Article).all()
        if articles != []:
            return articles
        else:
            raise NoResultFound
    except NoResultFound:
        return -1

def fetch_article(session, id):
    try:
        article = session.query(Article).filter(Article.article_id == id).one()
        return article
    except NoResultFound:
        return -1

def add_article(session, article):
    try:
        session.add(article)
        return 0
    except Exception as e:
        print(e)
        return -1

@app.route("/", methods=["GET"])
def index():
    articles = run_transaction(sessionmaker(bind=engine,expire_on_commit=False),
                    lambda s: fetch_articles(s))
    if articles != -1:
        return render_template("index.html", articles=articles, markdown = markdown, Markup = Markup)
    return render_template("empty.html")

@app.route("/article/create", methods=["GET"])
def get_article_form():
    form = PostForm()
    return render_template("create_article.html", form=form)

@app.route("/article/create", methods=["POST", "GET"])
@limiter.limit("1/minute", override_defaults=False)
def post_article():
    form = PostForm()
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        ip = request.environ['REMOTE_ADDR']
    else:
        ip = request.environ['HTTP_X_FORWARDED_FOR']
    print(ip)
    author = str(request.form["author"]) + " :" + ip
    title = str(request.form["title"])
    snippet = str(request.form["snippet"])
    content = form.pagedown.data
    print(content)
    article = Article(article_author=author, article_title=title, article_snippet=snippet, article_content=content)
    result = run_transaction(sessionmaker(bind=engine,expire_on_commit=False),
            lambda s: add_article(s, article))
    if result == 0:
        return redirect("/")
    else:
        return render_template("something_went_wrong.html")

@app.route("/article/<int:article_id>", methods=["GET"])
def get_one(article_id):
    article = run_transaction(sessionmaker(bind=engine,expire_on_commit=False),
                    lambda s: fetch_article(s, article_id))
    if article != -1:
        title = article.article_title
        author = article.article_author
        content = Markup(markdown.markdown(article.article_content))
        return render_template("article.html", title = title, author = author, content = content)
    return "Not Found", 404

if __name__ == "__main__":
    app.run()