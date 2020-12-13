
###################################################################################
# 
# doc sur cette app : https://www.digitalocean.com/community/tutorials/how-to-make-a-web-application-using-flask-in-python-3-fr
# export FLASK_APP=app
# export FLASK_ENV=development
# flask run
# http://127.0.0.1:5000/
#
###################################################################################

import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect
from werkzeug.exceptions import abort

###################################################################################
# .... Connexion à SQLite
###################################################################################
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

###################################################################################
# .... Démarrage du serveur Flask
###################################################################################
app = Flask(__name__)
app.config['SECRET_KEY'] = '1234'

###################################################################################
# .... endpoint / : index
###################################################################################
@app.route('/')
def index():
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM posts').fetchall()
    conn.close()
    return render_template('index.html', posts=posts)

###################################################################################
# .... Function getPost pour récupérer un post dans SQLite avec son ID
###################################################################################
def getPost(post_id):
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    conn.close()
    if post is None:
        abort(404)
    return post

###################################################################################
# .... endpoint /<id> : pour obtenir un post disrectement par son ID
###################################################################################
@app.route('/<int:post_id>')
def post(post_id):
    post = getPost(post_id)
    return render_template('post.html', post=post)

###################################################################################
# .... endpoint /create : pour le create un post
###################################################################################
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            conn = get_db_connection()
            conn.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))

    return render_template('create.html')

###################################################################################
# .... endpoint /<id>/edit : pour pouvoir editer un post
###################################################################################
@app.route('/<int:id>/edit', methods=('GET', 'POST'))
def edit(id):
    post = getPost(id)

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            conn = get_db_connection()
            conn.execute('UPDATE posts SET title = ?, content = ?'
                         ' WHERE id = ?',
                         (title, content, id))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))

    return render_template('edit.html', post=post)

###################################################################################
# .... endpoint /<id>/delete pour supprimer un post
###################################################################################
@app.route('/<int:id>/delete', methods=('POST',))
def delete(id):
    post = getPost(id)
    conn = get_db_connection()
    conn.execute('DELETE FROM posts WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('"{}" was successfully deleted!'.format(post['title']))
    return redirect(url_for('index'))
