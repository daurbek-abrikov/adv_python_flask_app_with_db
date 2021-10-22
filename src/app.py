from flask import Flask, render_template, request, flash
from flask.json import jsonify
from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
import jwt


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:root@localhost:5432/python_flask_users'
app.config['SECRET_KEY'] = 'thisismyflasksecretkey'

db = SQLAlchemy(app)


@app.route('/login', methods=['GET', 'POST'])
def login():
    login = request.form.get('login')
    password = request.form.get('password')

    user = User.query.filter_by(login=login).first() 

    if not user:
        flash('Please check your login details and try again.')
        return render_template('login.html')

    user_login = User.query.filter_by(login=login).first().login 
    user_pass = User.query.filter_by(login=login).first().password 

    if user_pass!=password:
        flash('Please check your login details and try again.')
        return render_template('login.html')

    if user_login==login and user_pass==password:
        token = jwt.encode({'user': login, 'exp':datetime.utcnow() + timedelta(minutes=30)}, app.config['SECRET_KEY'])

        user.token = token
        db.session.add(user)
        db.session.commit()
        return jsonify({'token': token})  
 
    return render_template('login.html')


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/protected')
def protect():
    token = request.args.get('token') 

    user = User.query.filter_by(token=token).first() 
    if user:
        return '<h1>Hello, token which is provided is correct {}</h1>'.format(token)
    return '<h1>Hello, Could not verify the token</h1>'
    

class User(db.Model):
    __tablename__ = 'User'
    id = db.Column('id', db.Integer, primary_key=True)
    login = db.Column('login', db.String(80), unique=True)
    password = db.Column('password', db.String(80))
    token = db.Column('token', db.String)

    def __init__(self, login, password, token):
        self.login = login
        self.password = password
        self.token = token

    def __repr__(self):
        return f"User('{self.login}', '{self.token}')"



db.drop_all()
db.create_all()

user1 = User(login='first_user', password='password', token='some_token')
user2 = User(login='second_user', password='password', token='some_token')
user3 = User(login='third_user', password='password', token='some_token')

db.session.add(user1)
db.session.add(user2)
db.session.add(user3)

db.session.commit()

if __name__ == "__main__":
    app.run()
