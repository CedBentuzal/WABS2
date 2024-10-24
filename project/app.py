from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///accounts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)


@app.route('/')
def loginpage():
    return render_template('login.html')
@app.route('/log_in', methods =['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        
        if user and user.password == password:
            
            return f"Welcome, {username}!"
        else:
            
            return "Error: Invalid username or password.", 401
    return

@app.route('/create_account')
def index():
    return render_template('index.html')

@app.route('/create_account', methods=['POST'])
def create_account():
    username = request.form.get('username')
    password = request.form.get('password')

    if not username or not password:
        return "Error: Username and password are required!", 400

    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return "Error: Username already exists!", 400

    
    new_user = User(username=username, password=password)
    db.session.add(new_user)
    db.session.commit()
    
    return f"Account created for {username}!"
    

@app.route('/accounts')
def accounts():
    users = User.query.all()
    return render_template('accounts.html', users=users)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()  
    app.run(debug=True)
