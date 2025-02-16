import os
from flask import Flask, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message as MailMessage
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email
from itsdangerous import URLSafeTimedSerializer as Serializer
from datetime import timedelta  # Add

app = Flask(__name__)

# Get secret key from environment variable or use default (for local development)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'Sandricksoni729')

# Use PostgreSQL database in production
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{os.environ.get("DB_USER")}:{os.environ.get("DB_PASSWORD")}@{os.environ.get("DB_HOST")}/{os.environ.get("DB_NAME")}'
db = SQLAlchemy(app)

# Flask-Mail Configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')  # Your email
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')  # Your email password
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_USERNAME')

mail = Mail(app)

# Project model
class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    link = db.Column(db.String(200), nullable=True)

# Message model
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())

# Contact form
class ContactForm(FlaskForm):
    name = StringField('სახელი', validators=[DataRequired()])
    email = StringField('ელ.ფოსტა', validators=[DataRequired(), Email()])
    message = TextAreaField('შეტყობინება', validators=[DataRequired()])
    submit = SubmitField('გაგზავნა')

# Verification email function
def send_verification_email(user_email):
    s = Serializer(app.config['SECRET_KEY'])
    token = s.dumps({'email': user_email})
    verification_link = url_for('verify_email', token=token, _external=True)

    msg = MailMessage(
        subject="📧 Email Verification",
        recipients=[user_email],
        body=f"Verification Link: {verification_link}"
    )
    mail.send(msg)

@app.route('/verify_email/<token>')
def verify_email(token):
    s = Serializer(app.config['SECRET_KEY'])
    try:
        data = s.loads(token, max_age=3600)
    except:
        return "The verification link is invalid or has expired."
    
    email = data['email']
    flash(f'Email {email} successfully verified!', 'success')
    return redirect(url_for('contact'))

@app.route('/contact', methods=['GET', 'POST']) 
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        send_verification_email(form.email.data)
        flash('Verification email sent! Please verify your email before submitting the message.', 'info')
        return redirect(url_for('contact'))
    return render_template('contact.html', form=form)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/portfolio')
def portfolio():
    projects = Project.query.all()
    return render_template('portfolio.html', projects=projects)

@app.route('/messages')
def view_messages():
    messages = Message.query.order_by(Message.timestamp.desc()).all()
    return render_template('messages.html', messages=messages)

# Initialize database tables on first run
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=False)  # Set to False for production
