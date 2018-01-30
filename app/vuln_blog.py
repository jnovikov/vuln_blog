from functools import wraps

import sqlite3
from flask import Flask
from flask import g
from flask import url_for
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for
from flask import make_response
from flask_bootstrap import Bootstrap

app = Flask(__name__)
app.secret_key = 'abcdefghijklmnoprst'
DATABASE = app.static_folder + '/../db.db'
Bootstrap(app)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.cookies.get('username'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)

    return decorated_function


def connect_to_database():
    return sqlite3.connect(DATABASE)


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = connect_to_database()
        db.row_factory = sqlite3.Row
    return db


def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


def query_db(query, args=(), one=False):
    query = query.format(*args)
    print(query)
    cur = get_db().execute(query)
    rv = cur.fetchall()
    get_db().commit()
    cur.close()
    return (rv[0] if rv else None) if one else rv


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route('/register', methods=['POST', 'GET'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')
    else:
        login = request.form['login']
        password = request.form['password']
        if not (login and password):
            return redirect(url_for('signup'))
        c = query_db('''select * from Users where name = '{}' ''', [login])
        print(c)
        if c:
            return redirect(url_for('signup'))
        else:
            query_db('''insert into users (name,password) values ('{}','{}')''', [login, password])
            return redirect(url_for('login'))


@app.route('/')
def index():
    username = request.cookies.get('username')
    if username is not None:
        return redirect('/posts')
    else:
        return render_template('index.html')


@app.route('/logout')
def logout():
    resp = make_response(redirect(url_for('index')))
    resp.set_cookie('username', '', expires=0)
    resp.set_cookie('id', '', expires=0)
    return resp


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        login = request.form['login']
        password = request.form['password']
        usr = query_db('''select * from Users where name = '{}' and  password = '{}' ''', [login, password], True)
        if usr is None:
            return redirect('/login')
        else:
            log = usr['name']
            id = str(usr['id'])

            resp = make_response(redirect('/posts'))
            resp.set_cookie('username', log)
            resp.set_cookie('id', id)
            return resp


@login_required
@app.route('/write', methods=['POST', 'GET'])
def create_post():
    print(request.form)
    if request.method == 'GET':
        return render_template('create_post.html')
    else:
        name = request.form['name']
        text = request.form['text']
        print(name, text)
        if not (name and text):
            return redirect('/create')
        id = request.cookies.get('id')
        query_db('''insert into Posts (name,text,author_id) values ('{}','{}','{}') ''', [name, text, id])
        return redirect('/posts')


@login_required
@app.route('/posts')
def posts():
    id = request.cookies.get('id')
    print(id, type(id))
    posts = query_db('''select * from Posts where author_id = {} ''', [id])
    print(posts)
    return render_template("posts.html", posts=posts)


@app.route('/post-<p_id>')
def current_post(p_id):
    post = query_db('''select * from Posts where id = {}''', [p_id], True)
    if post is None:
        return "Post not found", 404
    return render_template('post.html', name=post['name'], text=post['text'])


