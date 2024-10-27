from flask import Flask, redirect, request, render_template, session, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Needed for session management

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///accounts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    balance = db.Column(db.Float, default=0)

@app.route('/')
def loginpage():
    return render_template('login.html')

@app.route('/log_in', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            session['username'] = username  # Store the username in session
            return redirect(url_for('user'))
        else:
            return "Error: Invalid username or password.", 401


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

@app.route('/accounts', methods=['GET', 'POST'])
def accounts():
    if request.method == 'POST':
        user_id = request.form.get('user_id')  
        action = request.form.get('action')  

        
        user = User.query.get(user_id)

        if action == "Update Balance":
            
            balance = request.form.get('balance', type=float)  

            if user:
                user.balance = balance  
                db.session.commit()  
                return f"User's balance updated to ${balance}!", 200
            return "Error: User not found.", 404
        
        elif action == "Delete Account":
            
            if user:
                db.session.delete(user)  
                db.session.commit()  
                return "User deleted successfully!", 200
            return "Error: User not found.", 404

    
    users = User.query.all()
    return render_template('accounts.html', users=users)


@app.route('/user', methods=['GET','POST'])
def user():
    username = session.get("username")
    user = User.query.filter_by(username=username).first()
    if user:
        return render_template('user.html', user=user)
    else:
        return redirect(url_for('loginpage'))

@app.route('/send', methods=['POST'])
def send():
    sender_username = session.get("username")  
    recipient_username = request.form.get('recipient')
    amount = float(request.form.get('amount'))

    sender = User.query.filter_by(username=sender_username).first()
    recipient = User.query.filter_by(username=recipient_username).first()

    if not sender or not recipient:
        return "Error: User not found.", 404

    if sender.balance < amount:
        return "Error: Insufficient balance.", 400

    sender.balance -= amount
    recipient.balance += amount
    db.session.commit()

    return f"Sent ${amount} to {recipient_username}!"

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

