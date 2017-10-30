from flask import Flask, request, redirect, render_template, session, redirect, flash
from flask_sqlalchemy import SQLAlchemy
import string

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:arsenal@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'fNLjA7Y7V4EzM1'


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(500))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):

        self.username = username
        self.password = password


@app.before_request
def require_login():
    allowed_routes = ['login', 'signup','blog','index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


@app.route('/main', methods=['GET'])
def index():

    all_users = User.query.all()
    return render_template('index.html', all_users=all_users)


@app.route('/login', methods=['POST','GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash(username + " has been logged in")
            return redirect('/blog')
            

        else:
            flash('User name or password incorrect, or does not exist.')


    return render_template('login.html')


@app.route('/signup', methods=['POST','GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        if len(username) is 0 or len(password) is 0:
            flash("Must provide username and password!")
            return render_template('signup.html', username=username, password=password)

        if password != verify:
            flash('Passwords do not match!')
            return render_template('signup.html', username=username)

        if len(username)<3 or len(password)<3:
            flash('Username and password must be atleast 3 characters in length!')
            return render_template('signup.html', username=username)
    
        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/blog')

        else:
            flash('User already exist!')
            return render_template('signup.html')    
    
    return render_template('signup.html')


@app.route('/blog', methods=['POST', 'GET'])
def blog():
    blog_id=request.args.get('id')
    user_id=request.args.get('user')
    
    
    if blog_id:
        blog_entry=Blog.query.get(blog_id)
        return render_template('blog_entry.html', blog_entry=blog_entry)
    
    if user_id:
        user_entry=User.query.get(user_id)
        return render_template("single-user.html",user=user_entry)
    
    new_post = Blog.query.all()
    return render_template('blog.html', new_post=new_post)

@app.route('/newpost', methods=['POST','GET'])
def new_post(): 
    if request.method == "GET":
        return render_template('new-post.html')
        
    if request.method == 'POST':
        blog_title = request.form['title']
        blog_content = request.form['body']
        owner = User.query.filter_by(username=session['username']).first()
        new_blog = Blog(blog_title, blog_content, owner)

        if len(blog_title) is 0 or len(blog_content) is 0:
            flash("Blog title and content must be filled!", 'error')    
            return render_template("new-post.html", blog_title=blog_title, blog_content=blog_content)
        

        else: 
            db.session.add(new_blog)
            db.session.commit()
            url = "/blog?id=" + str(new_blog.id)
            return redirect(url)
            
            


@app.route('/logout')
def logout():
    username = str(session['username'])
    del session['username']
    flash(username + " has been logged out")
    return redirect('/main')

if __name__ == "__main__":
    app.run()