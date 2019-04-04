from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from secret import secret_key, api_key, config_db

# !!!store api key in .gitignore!!!
app = Flask(__name__)
app.config['DEBUG'] = True
secret.config_db()
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
secret.secret_key()
#for generated tweets - store in db
class Tweet(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    tweet = db.Column(db.String(180))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, tweet, owner):
        self.tweet = tweet
        self.owner = owner

#Stores user information
#need to store oauth token
class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    tw_handle = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    owner = db.relationship('Blog', backref='owner')

    def __init__(self, tw_handle, password):
        self.tw_handle=tw_handle
        self.password=password

# don't think I need this - saving jic
# @app.route('/single-tweet')
# def single_user():
#     single_user_blog = request.args.get('user')
#     single_user_entries = Blog.query.filter_by(owner_id=single_user_blog).all()
#     owners = User.query.filter_by(id=single_user_blog).all()
#     single_blog = request.args.get('id')
#     single_blog_entry = Blog.query.filter_by(id=single_blog).all()
#
#     return render_template('singleUser.html',title="Single User's Blog", single_user_blog=single_user_blog,single_blog=single_blog, single_user_entries=single_user_entries,owners=owners,single_blog_entry=single_blog_entry)


#existing user login
@app.route('/login', methods=['POST','GET'])
def login():
    if request.method == 'POST':
        tw_handle = request.form['tw_handle']
        password = request.form['password']
        user = User.query.filter_by(tw_handle=tw_handle).first()
        if user and user.password == password:
            #remember that the user has logged in
            session['tw_handle'] = tw_handle
            flash('Logged in!')
            return redirect('/newpost')
        elif not user:
            flash('User does not exist', 'error')
        else:
            flash('User password incorrect','error')

    return render_template('login.html')

#register new user and get token
#need to make an api call and get an oath2 token
@app.route('/register', methods=['POST','GET'])
def register():
    if request.method == 'POST':
        tw_handle = request.form['tw_handle']
        password = request.form['password']
        verify = request.form['verify_password']

        #TODO - make sure username (tw_handle) exists within twitter?
        #might be able to eliminate pw and use twitter token

        #twitter acct needs @ and 3-16 char long
        if len(tw_handle) < 3 or len(tw_handle) > 16 or '@' not in tw_handle:
            tw_handle = form.format(tw_handle)
            tw_handle = ''
            flash('This is not a valid username.','error')
            return render_template('register.html')
        #need pw to be at least 3-20 char long
        if len(password) < 3 or len(password) > 20:
            flash('Your password must be between 3 and 20 characters','error')
            return render_template('register.html')
        #need verify==pw
        if verify != password:
            flash('Verify password must match your password','error')
            return render_template('register.html')

        existing_user = User.query.filter_by(tw_handle=tw_handle).first()
        if not existing_user:
            new_user = User(tw_handle,password)
            db.session.add(new_user)
            db.session.commit()
            session['tw_handle'] = tw_handle
            return redirect('/newpost')

        else:
            flash('User already exists', 'error')
            return render_template('register.html', title='Register')

    return render_template('register.html', title='Register')

@app.route('/logout')
def logout():
    del session['tw_handle']
    return redirect('/tweet')

@app.route('/tweet', methods=['POST','GET'])
def new_post():
    if 'tw_handle' not in session:
        return redirect('/login')
    else:
        owner = User.query.filter_by(tw_handle=session['tw_handle']).first()

        if request.method =='POST':
            blog_title = request.form['blog-title']
            blog_entry = request.form['blog-entry']
            if len(blog_title) == 0:
                flash('You must give this entry a title', 'error')
                return render_template('newpost.html',title='New Post')

            elif len(blog_entry) == 0:
                flash('You must write an entry', 'error')
                return render_template('newpost.html',title='New Post')
            else:
                new_blog = Blog(blog_title, blog_entry, owner)
                db.session.add(new_blog)
                db.session.commit()
                id = str(new_blog.id)
                new_url = '/tweet?id='+id
                return redirect(new_url)

        return render_template('newpost.html',title='New Post')

@app.route('/all-tweets', methods=['POST','GET'])
def list_blogs():
    blogs = Tweet.query.all()
    single_user_id = request.args.get('user')
    single_blog = request.args.get('id')
    single_blog_entry = Blog.query.filter_by(id=single_blog).all()
    owners = User.query.all()

    if 'tw_handle' in session:
        owner = User.query.filter_by(tw_handle=session['tw_handle']).first()
        return render_template('blog.html',title='Build A Blog',single_blog_entry=single_blog_entry, single_blog=single_blog, blogs=blogs, owners=owners,single_user_id=single_user_id)
    return render_template('blog.html',title='Build A Blog',single_blog_entry=single_blog_entry, single_blog=single_blog, blogs=blogs, owners=owners, single_user_id=single_user_id)



@app.route('/', methods=['POST','GET'])
def index():
    tw_handles = User.query.all()

    return render_template('index.html',title='Home',tw_handles=tw_handles)

if __name__ == '__main__':
    app.run()
